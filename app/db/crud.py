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
        new_jetson = models.Jetson(**jetson_data)
        db.add(new_jetson)
        db.commit()
        db.refresh(new_jetson)
        return new_jetson
    else:
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
    jetson = db.query(models.Jetson).first()
    if not jetson:
        return None
        
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
#  [3단계] 카메라 2단계 등록 및 조회 로직
# ==========================================
def register_camera_info(db: Session, ip_address: str, camera_id: str, camera_pw: str):
    """카메라 중복을 검사하고 DB에 자동 생성된 이름/위치와 함께 저장합니다."""
    # 1. 중복 검사 (같은 ip_address의 db가 있는지 비교)
    existing_camera = db.query(models.CameraInfo).filter(models.CameraInfo.ip_address == ip_address).first()
    if existing_camera:
        return None  

    jetson = db.query(models.Jetson).first()
    if not jetson:
        return False

    # 2. 센서 테이블에 먼저 등록 (이름/위치 자동 생성)
    new_sensor = models.Sensor(
        jetson_id=jetson.jetson_id,
        sensor_type="camera",
        sen_name=f"CAM_{ip_address.split('.')[-1]}", 
        sen_locate=jetson.jetson_loc,                
        register_date=datetime.now().date()
    )
    db.add(new_sensor)
    db.flush() 

    # 3. 카메라 정보 테이블에 등록 (health 자동 1 배정)
    new_camera = models.CameraInfo(
        sen_id=new_sensor.sen_id,
        ip_address=ip_address,
        camera_id=camera_id,
        camera_pw=camera_pw
    )
    db.add(new_camera)
    db.commit() 
    return new_camera

def get_cctv_list(db: Session):
    """CameraInfo와 Sensor 테이블을 Join하여 목록을 반환합니다."""
    results = db.query(
        models.CameraInfo.ip_address,
        models.CameraInfo.health,
        models.Sensor.sen_name,
        models.Sensor.sen_locate
    ).join(models.Sensor, models.CameraInfo.sen_id == models.Sensor.sen_id).all()
    
    return results

# ==========================================
#  [수정] 센서 목록 조회 로직 (카메라 제외)
# ==========================================
def get_sensor_list(db: Session):
    """Sensor 테이블에서 'camera' 타입을 제외한 등록된 모든 센서의 목록을 반환합니다."""
    results = db.query(
        models.Sensor.sen_name,
        models.Sensor.sensor_type,
        models.Sensor.sen_locate
    ).filter(
        models.Sensor.sensor_type != "camera"  # 🌟 핵심: camera 타입은 제외!
    ).all()
    
    return results