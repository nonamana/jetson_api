from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.db import models
from app import schemas

# ==========================================
#  [1단계] 젯슨 장비 및 앱 연결 로직
# ==========================================
def init_jetson_info(db: Session, jetson_data: dict):
    """서버 부팅 시 젯슨 초기 정보를 세팅하고 최신 IP로 업데이트합니다."""
    existing = db.query(models.Jetson).first()
    
    if not existing:
        # 정보가 아예 없으면 새로 저장
        new_jetson = models.Jetson(**jetson_data)
        db.add(new_jetson)
        db.commit()
        db.refresh(new_jetson)
        return new_jetson
    else:
        # 정보가 이미 있으면 IP와 포트만 최신 상태로 갱신
        existing.ip_addr = jetson_data["ip_addr"]
        existing.port = jetson_data["port"]
        db.commit()
        db.refresh(existing)
        return existing

def get_jetson_info(db: Session):
    """DB에 저장된 젯슨 정보를 하나 꺼내옵니다."""
    return db.query(models.Jetson).first()

def register_jetson_connection(db: Session, req: schemas.JetsonRegisterReq):
    """POST /api/jetson/register 호출 시 connect 테이블에 사번과 앱 연결 기록"""
    # 1. 현재 젯슨의 정보를 불러옴
    jetson = db.query(models.Jetson).first()
    if not jetson:
        return None
        
    # 2. connect 테이블에 관리자 사번과 젯슨 연결 기록 (DB 저장)
    new_connect = models.Connect(
        dept_id=req.dept_id,
        jetson_id=jetson.jetson_id,
        app_id=req.app_id
    )
    db.add(new_connect)
    db.commit()
    
    return jetson

# ==========================================
#  [2단계] 센서 다중 등록 로직
# ==========================================
def register_multiple_sensors(db: Session, jetson_id: int, sensors: List[schemas.SensorItem]):
    """배열(List) 형태로 들어온 다수의 센서를 한 번에 DB에 저장합니다."""
    db_sensors = []
    for s in sensors:
        new_sensor = models.Sensor(
            jetson_id=jetson_id,
            sensor_type=s.sensor_type,
            sen_name=s.sen_name,
            sen_locate=s.sen_locate,
            mqtt_topic=s.mqtt_topic
        )
        db.add(new_sensor)
        db_sensors.append(new_sensor)
    db.commit()
    return db_sensors

# ==========================================
#  [3단계] 카메라 2단계 등록 로직
# ==========================================
def register_camera_info(db: Session, camera_id: str, camera_pw: str):
    """카메라를 센서로 먼저 등록하고, 발급된 sen_id로 카메라 상세 정보를 저장합니다."""
    # 1. 젯슨 정보 가져오기 (ip_addr, jetson_wp 활용)
    jetson = db.query(models.Jetson).first()
    if not jetson:
        return None

    # 2. [1단계 DB] 센서 테이블에 먼저 등록 (sen_id를 얻기 위함)
    new_sensor = models.Sensor(
        jetson_id=jetson.jetson_id,
        sensor_type="camera",
        sen_name="camera-name",
        sen_locate=jetson.jetson_wp,
        register_date=datetime.utcnow().date()
    )
    db.add(new_sensor)
    db.flush() 

    # 3. [2단계 DB] 발급받은 sen_id를 외래키로 사용하여 카메라 정보 등록
    new_camera = models.CameraInfo(
        sen_id=new_sensor.sen_id,
        ip_address=jetson.ip_addr,
        camera_id=camera_id,
        camera_pw=camera_pw
    )
    db.add(new_camera)
    db.commit() 
    
    return new_camera

# ==========================================
#  [4단계] 위험 이벤트 DB 저장 로직
# ==========================================
def create_hazard_event(db: Session, req: schemas.VlmAnalysisReq):
    """VLM에서 넘어온 위험 정보를 Event 테이블에 저장합니다."""
    # 1. 이벤트 코드 확인 (없으면 임시 생성 - 외래키 에러 방지)
    ev_code = db.query(models.EventCode).filter(models.EventCode.ev_code_name == req.ev_code_name).first()
    if not ev_code:
        ev_code = models.EventCode(ev_code_name=req.ev_code_name, ev_code_desc="자동 생성된 위험 코드")
        db.add(ev_code)
        db.flush()

    # 2. 해당 카메라(센서) 정보 찾기
    sensor = db.query(models.Sensor).filter(models.Sensor.sen_name == req.camera_name).first()
    sen_id = sensor.sen_id if sensor else None

    # 3. 이벤트 기록 저장
    new_event = models.Event(
        ev_code_id=ev_code.ev_code_id,
        sen_id=sen_id,
        message=req.risk_text,
        time=datetime.now() # 테스트 편의를 위해 현재 서버 시간으로 저장
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return new_event
# (2~4단계용 함수들은 다음 단계에서 차례대로 추가하겠습니다!)