from sqlalchemy.orm import Session
from app.db import models
from app import schemas

# 1. 젯슨 장비 등록
def init_jetson_info(db: Session, jetson_data: dict):
    """서버 부팅 시 젯슨 초기 정보를 세팅합니다 (중복 방지)."""
    # 이미 정보가 있는지 확인 (서버 껐다 켤 때마다 에러 나는 것 방지)
    existing = db.query(models.Jetson).first()
    
    if not existing:
        # 정보가 없으면 새로 저장
        new_jetson = models.Jetson(**jetson_data)
        db.add(new_jetson)
        db.commit()
        db.refresh(new_jetson)
        return new_jetson
    return existing

def get_jetson_info(db: Session):
    """DB에 저장된 젯슨 정보를 하나 꺼내옵니다."""
    return db.query(models.Jetson).first()

# 2. 센서 등록 (심박/온습도 등)
def create_sensor(db: Session, sensor: schemas.SensorCreate):
    # 여기서도 schemas의 sen_status와 models의 sen_status가 일치하므로 자동 매핑!
    db_sensor = models.Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def get_all_sensors(db: Session):
    return db.query(models.Sensor).all()

def create_camera(db: Session, cam_data: schemas.CameraCreate):
    # 센서 테이블에 먼저 등록 (외래키 및 상태 컬럼 제거 반영)
    db_sensor = models.Sensor(
        sensor_type=cam_data.sensor_type,
        sen_name=cam_data.sen_name,
        mqtt_topic=cam_data.mqtt_topic
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)

    # 카메라 정보 테이블에 등록 (sen_id 외래키는 그대로 유지)
    db_camera = models.CameraInfo(
        sen_id=db_sensor.sen_id,
        ip_address=cam_data.ip_address,
        camera_id=cam_data.camera_id,
        camera_pw=cam_data.camera_pw
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    
    return db_sensor