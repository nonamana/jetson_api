from sqlalchemy.orm import Session
from app.db import models
from app import schemas

# 1. 젯슨 장비 등록
def create_jetson(db: Session, jetson: schemas.JetsonCreate):
    # **jetson.model_dump()는 schemas와 models의 변수명이 100% 같아야 작동합니다.
    # 우리 아까 둘 다 jetson_status로 맞춰놨으니 아주 잘 작동할 거예요!
    db_jetson = models.Jetson(**jetson.model_dump())
    db.add(db_jetson)
    db.commit()
    db.refresh(db_jetson)
    return db_jetson

# 2. 센서 등록 (심박/온습도 등)
def create_sensor(db: Session, sensor: schemas.SensorCreate):
    # 여기서도 schemas의 sen_status와 models의 sen_status가 일치하므로 자동 매핑!
    db_sensor = models.Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

# 3. 특정 젯슨에 연결된 센서 목록 조회
def get_sensors_by_jetson(db: Session, jetson_id: int):
    return db.query(models.Sensor).filter(models.Sensor.jetson_id == jetson_id).all()

# 4. 카메라 등록 (센서 테이블 + 카메라 정보 테이블 두 군데 저장)
def create_camera(db: Session, cam_data: schemas.CameraCreate):
    # (1) 센서(Sensor) 테이블에 기본 정보 먼저 저장
    db_sensor = models.Sensor(
        sensor_type=cam_data.sensor_type,
        sen_name=cam_data.sen_name,
        sen_status=cam_data.sen_status, # 🔍 수정: status -> sen_status
        jetson_id=cam_data.jetson_id
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)

    # (2) 카메라 정보(CameraInfo) 테이블에 세부 정보 저장 (FK: sen_id 사용)
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