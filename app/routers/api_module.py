from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app import schemas

# 🌟 나중에 안전 감지 모듈 작성 시 주석을 해제하고 연결하세요.
# from app.safety.safety_module import process_hazard_event 

router = APIRouter(prefix="/api", tags=["API 호출 모듈"])

# ==========================================
#  스마트폰 앱 전용 요청 스키마 (Request Body)
# ==========================================
class AppCameraReq(BaseModel):
    ip_address: str
    camera_id: str
    camera_pw: str


# ==========================================
#  [1단계] 젯슨 장비 등록 및 앱 연동 API
# ==========================================
@router.post("/jetson/register", response_model=schemas.JetsonRegisterRes, summary="젯슨 등록 및 앱 연동")
def register_jetson(req: schemas.JetsonRegisterReq, db: Session = Depends(get_db)):
    """관리자 앱에서 사번과 앱 ID를 보내면 젯슨 접속 정보를 반환합니다."""
    jetson = crud.register_jetson_connection(db, req)
    
    if not jetson:
        raise HTTPException(status_code=404, detail="DB에 젯슨 초기 정보가 없습니다.")
        
    return schemas.JetsonRegisterRes(
        jetson_id=f"jetson-{jetson.jetson_id:02d}",
        register_status="success",
        api_base_url=f"http://{jetson.ip_addr}:{jetson.port}",
        ws_url=f"ws://{jetson.ip_addr}:{jetson.port}/ws/alerts"
    )


# ==========================================
#  [2단계] 센서 감지 및 다중 등록 API
# ==========================================
@router.get("/sensors/discovered", response_model=schemas.DiscoveredSensorsRes, summary="mDNS 감지 센서 목록 조회")
def get_discovered_sensors():
    """mDNS로 주변에서 감지된 센서 목록(더미)을 앱에 전달합니다."""
    dummy_sensors = [
        schemas.SensorItem(sen_name="손목밴드1", sensor_type="heart_rate", mqtt_topic="sensor/band-01/heart_rate", sen_locate="locate1"),
        schemas.SensorItem(sen_name="온습도계1", sensor_type="temperature_humidity", mqtt_topic="sensor/temp-01/data", sen_locate="locate1")
    ]
    return schemas.DiscoveredSensorsRes(jetson_id="jetson-01", discovered_sensors=dummy_sensors)

@router.post("/sensors/register", summary="센서 다중 등록")
def register_sensors(req: schemas.SensorRegisterReq, db: Session = Depends(get_db)):
    """앱에서 선택한 여러 개의 센서를 한 번에 DB에 저장합니다."""
    try:
        j_id = int(req.jetson_id.split("-")[1])
    except:
        j_id = 1 
        
    crud.register_multiple_sensors(db, jetson_id=j_id, sensors=req.selected_sensors)
    return {"status": "success", "message": "Sensors registered successfully"}


# ==========================================
#  [3단계] 카메라 등록 및 조회 API
# ==========================================
@router.post("/cameras/register", summary="카메라 등록 및 VLM 중계")
def register_camera(req: AppCameraReq, db: Session = Depends(get_db)):
    """앱에서 받은 IP 정보를 DB에 저장하고 VLM 서버로 전달할 데이터를 로그에 찍습니다."""
    camera_info = crud.register_camera_info(db, req.ip_address, req.camera_id, req.camera_pw)
    
    if camera_info is None:
        raise HTTPException(status_code=400, detail="이미 등록된 카메라입니다.")
    elif camera_info is False:
        raise HTTPException(status_code=404, detail="젯슨 정보가 DB에 없습니다.")
        
    vlm_payload = {
        "ip_address": camera_info.ip_address,
        "camera_id": camera_info.camera_id,
        "camera_pw": camera_info.camera_pw,
        "rtsp_port": 554,
        "rtsp_path": "/stream1"
    }
    print(f"📡 [VLM 서버로 전송됨 (Mock)]: {vlm_payload}")
    
    return {"status": "success", "message": "카메라가 성공적으로 등록되었습니다."}

@router.get("/cameras", summary="CCTV 목록 조회")
def get_cameras(db: Session = Depends(get_db)):
    """스마트폰에서 CCTV 목록을 볼 때 호출됩니다."""
    cctv_list = crud.get_cctv_list(db)
    result_data = []
    for cctv in cctv_list:
        result_data.append({
            "ip_address": cctv.ip_address,
            "sen_name": cctv.sen_name,
            "sen_locate": cctv.sen_locate,
            "health": cctv.health
        })
    return {"status": "success", "data": result_data}

# ==========================================
#  [추가] 일반 센서 목록 조회 API (카메라 제외)
# ==========================================
@router.get("/sensors", summary="등록된 일반 센서 목록 조회")
def get_sensors(db: Session = Depends(get_db)):
    """스마트폰에서 센서 목록을 볼 때 호출됩니다 (카메라 제외)."""
    sensor_list = crud.get_sensor_list(db)
    result_data = []
    for sensor in sensor_list:
        result_data.append({
            "sen_name": sensor.sen_name,
            "sensor_type": sensor.sensor_type,
            "sen_locate": sensor.sen_locate
        })
    return {"status": "success", "data": result_data}

# ==========================================
#  [4단계] 위험 분석 정보 수신 및 내부 토스 API : 안전 감지 모듈 추가 시 수정
# ==========================================
@router.post("/internal/vlm-analysis", summary="위험 감지 데이터 안전 감지 모듈로 전달")
async def receive_vlm_analysis(req: schemas.VlmAnalysisReq, background_tasks: BackgroundTasks):
    """
    VLM에서 보낸 위험 정보를 받아서 내부 안전 감지 모듈로 토스합니다.
    웹소켓 푸시와 DB 저장은 안전 감지 모듈이 백그라운드에서 처리합니다.
    """
    # 🌟 나중에 안전 감지 모듈 개발 시 아래 주석을 풀고 호출하세요.
    # background_tasks.add_task(process_hazard_event, req)
    
    print(f"📡 [API 모듈] VLM 데이터 수신 및 내부 전달: {req.camera_name}")
    
    # VLM 모듈에게는 텍스트 없이 200 OK만 즉시 응답
    return Response(status_code=status.HTTP_200_OK)

# ==========================================
#   웹소켓 연결 매니저 (Session 관리)
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
        """내부 모듈(예: 위험 전달 모듈)이 이 함수를 호출해서 알림을 쏩니다!"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

# 메인 파일과 다른 모듈에서 쓸 수 있도록 인스턴스화
manager = ConnectionManager()