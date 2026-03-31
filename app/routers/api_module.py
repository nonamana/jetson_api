from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app import schemas

router = APIRouter(prefix="/api", tags=["API 호출 모듈"])

# ==========================================
#  [1단계] 젯슨 장비 등록 및 앱 연동 API
# ==========================================
@router.post("/jetson/register", response_model=schemas.JetsonRegisterRes, summary="젯슨 등록 및 앱 연동")
def register_jetson(req: schemas.JetsonRegisterReq, db: Session = Depends(get_db)):
    """
    관리자 앱에서 사번(dept_id)과 앱 이름(app_id)을 보내면,
    DB의 connect 테이블에 기록하고 젯슨 접속 정보를 반환합니다.
    """
    # 1. crud를 통해 데이터베이스에 연결 정보 저장
    jetson = crud.register_jetson_connection(db, req)
    
    # 2. 젯슨 정보가 DB에 없다면 에러 반환
    if not jetson:
        raise HTTPException(status_code=404, detail="DB에 젯슨 초기 정보가 없습니다.")
        
    # 3. 명세서에 맞춘 JSON 응답 반환
    return schemas.JetsonRegisterRes(
        jetson_id=f"jetson-{jetson.jetson_id:02d}", # 숫자 1을 "jetson-01" 형태로 변환
        register_status="success",
        api_base_url=f"http://{jetson.ip_addr}:{jetson.port}",
        ws_url=f"ws://{jetson.ip_addr}:{jetson.port}/ws/alerts"
    )

# ==========================================
#  [2단계] 센서 감지 및 다중 등록 API
# ==========================================
@router.get("/sensors/discovered", response_model=schemas.DiscoveredSensorsRes, summary="mDNS 감지 센서 목록 조회")
def get_discovered_sensors():
    """
    (임시) mDNS로 주변에서 감지된 센서 목록을 앱에 전달합니다.
    기획서 명세에 맞춰 더미 데이터를 반환합니다.
    """
    dummy_sensors = [
        schemas.SensorItem(sen_name="손목밴드1", sensor_type="heart_rate", mqtt_topic="sensor/band-01/heart_rate", sen_locate="locate1"),
        schemas.SensorItem(sen_name="온습도계1", sensor_type="temperature_humidity", mqtt_topic="sensor/temp-01/data", sen_locate="locate1")
    ]
    return schemas.DiscoveredSensorsRes(
        jetson_id="jetson-01", 
        discovered_sensors=dummy_sensors
    )

@router.post("/sensors/register", summary="센서 다중 등록")
def register_sensors(req: schemas.SensorRegisterReq, db: Session = Depends(get_db)):
    """앱에서 선택한 여러 개의 센서를 한 번에 DB에 저장합니다."""
    # "jetson-01" 같은 문자열에서 숫자(1)만 추출하여 DB에 매핑
    try:
        j_id = int(req.jetson_id.split("-")[1])
    except:
        j_id = 1 
        
    crud.register_multiple_sensors(db, jetson_id=j_id, sensors=req.selected_sensors)
    return {"message": "Sensors registered successfully"}

from pydantic import BaseModel

# 앱에서 보내는 카메라 등록 요청 규격 (임시 추가)
class AppCameraReq(BaseModel):
    camera_id: str
    camera_pw: str

# ==========================================
#  [3단계] 카메라 등록 및 VLM 서버 중계 API
# ==========================================
@router.post("/cameras/register", summary="카메라 등록 및 VLM 중계")
def register_camera(req: AppCameraReq, db: Session = Depends(get_db)):
    """
    앱에서 카메라 ID/PW를 받으면 DB에 2단계로 저장하고,
    VLM(카메라 제어 관리 모듈)로 RTSP 연결 정보를 전달합니다.
    """
    # 1. DB에 카메라 센서 및 카메라 정보 2단계 저장
    camera_info = crud.register_camera_info(db, req.camera_id, req.camera_pw)
    if not camera_info:
        raise HTTPException(status_code=404, detail="젯슨 정보가 DB에 없습니다.")
        
    # 2. VLM 서버로 보낼 JSON 페이로드 조립 (명세서 규격)
    vlm_payload = {
        "ip_address": camera_info.ip_address,
        "camera_id": camera_info.camera_id,
        "camera_pw": camera_info.camera_pw,
        "rtsp_port": 554,
        "rtsp_path": "/stream1"
    }
    
    # 3. VLM 서버와 통신 (현재는 테스트를 위해 더미 응답으로 대체)
    # -----------------------------------------------------------
    # [실제 구현 시 들어갈 코드]
    # import httpx
    # response = httpx.post("http://127.0.0.1:9000/vlm/api/camera/register", json=vlm_payload)
    # return response.json()
    # -----------------------------------------------------------
    
    print(f"📡 [VLM 서버로 전송됨 (Mock)]: {vlm_payload}")
    
    # VLM 서버가 RTSP 연결에 성공했다고 가정하고 앱에 응답 반환
    return {
        "status": "success",
        "sen_id": camera_info.sen_id,
        "message": "RTSP 연결 성공"
    }

# ==========================================
#  [4단계] 웹소켓 연결 매니저 (Global)
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """연결된 모든 스마트폰으로 실시간 푸시 알림을 쏩니다!"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# ==========================================
#  [4단계] 위험 분석 정보 수신 및 푸시 API
# ==========================================
@router.post("/internal/vlm-analysis", summary="위험 감지 및 실시간 푸시 알림")
async def receive_vlm_analysis(req: schemas.VlmAnalysisReq, db: Session = Depends(get_db)):
    """VLM 서버가 위험을 감지하면 호출! -> DB에 저장하고 앱으로 웹소켓 알림을 쏩니다."""
    # 1. 이벤트 DB 저장
    event_record = crud.create_hazard_event(db, req)

    # 2. 앱으로 보낼 알림 규격(Payload) 조립
    payload = {
        "type": "danger_alert",
        "event_id": event_record.event_id,
        "event_code": req.ev_code_name,
        "message": req.risk_text
    }

    # 3. 연결된 모든 스마트폰(웹소켓)에 경고 쏘기!
    await manager.broadcast(payload)
    print(f"🚨 [위험 발생!] 앱으로 푸시 알림 전송 완료: {payload}")

    return {"status": "success", "message": "Alert pushed to app"}
# ----------------------------------------------------
# 💡 아래 2~4단계 API들은 아직 구현 전이라 주석 처리 해두었습니다.
# (이대로 두셔야 서버 켤 때 에러가 나지 않습니다!)
# ----------------------------------------------------

# @router.get("/sensors/discovered", ...)
# @router.post("/sensors/register", ...)
# @router.post("/cameras/register", ...)
# @router.post("/internal/vlm-analysis", ...)