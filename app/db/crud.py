from sqlalchemy.orm import Session
from app.db import models
from app import schemas

def create_jetson(db: Session, jetson: schemas.JetsonCreate):
    db_jetson = models.Jetson(**jetson.model_dump())
    db.add(db_jetson)
    db.commit()
    db.refresh(db_jetson)
    return db_jetson

def create_sensor(db: Session, sensor: schemas.SensorCreate):
    db_sensor = models.Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def get_sensors_by_jetson(db: Session, jetson_id: int):
    return db.query(models.Sensor).filter(models.Sensor.jetson_id == jetson_id).all()

def create_camera(db: Session, cam_data: schemas.CameraCreate):
    # 1. 센서 테이블에 먼저 등록 (FK 연결을 위해)
    db_sensor = models.Sensor(
        sensor_type=cam_data.sensor_type,
        sen_name=cam_data.sen_name,
        status=cam_data.status,
        jetson_id=cam_data.jetson_id
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)

    # 2. 카메라 정보 테이블에 등록
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