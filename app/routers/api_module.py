from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud
from app import schemas

router = APIRouter(prefix="/api", tags=["API 호출 모듈"])

@router.get("/jetson", response_model=schemas.JetsonResponse, summary="젯슨 장비 정보 조회")
def get_jetson(db: Session = Depends(get_db)):
    """
    스마트폰 앱에서 이 주소로 GET 요청을 보내면,
    젯슨이 미리 저장해둔 자기 자신의 정보를 뱉어냅니다.
    """
    jetson_info = crud.get_jetson_info(db)
    
    # 혹시라도 DB에 정보가 없다면 404 에러 반환
    if not jetson_info:
        raise HTTPException(status_code=404, detail="젯슨 정보가 DB에 없습니다.")
        
    return jetson_info

@router.post("/sensors", response_model=schemas.SensorResponse, summary="센서 등록 (심박/온습도)")
def register_sensor(request: schemas.SensorCreate, db: Session = Depends(get_db)):
    """관리자 앱에서 센서를 젯슨에 할당합니다."""
    # 내부적으로 schemas.SensorCreate의 sen_status를 사용하게 됨
    return crud.create_sensor(db, request)

@router.post("/cameras", summary="CCTV 카메라 등록")
def register_camera(request: schemas.CameraCreate, db: Session = Depends(get_db)):
    """앱에서 IP 카메라 정보를 등록합니다. 이후 내부 모듈로 연결 정보를 토스할 수 있습니다."""
    sensor = crud.create_camera(db, request)
    return {"message": "Camera registered successfully", "sen_id": sensor.sen_id}

@router.get("/sensors", response_model=List[schemas.SensorResponse], summary="구독할 센서 목록 조회")
def get_sensors(db: Session = Depends(get_db)):
    """현재 젯슨에 등록된 모든 센서(MQTT 구독 대상) 목록을 가져옵니다."""
    return crud.get_all_sensors(db)

@router.post("/hazard/alert", summary="위험 정보 중계 (앱 알림 발송)")
def trigger_hazard_alert(alert: schemas.HazardAlert, db: Session = Depends(get_db)):
    """
    안전 감지 모듈이나 카메라 모듈이 위험을 감지하면 이 API를 호출합니다.
    API 서버는 이 정보를 받아 스마트폰 앱으로 푸시 알림을 전달합니다.
    """
    # 🔍 변경 포인트: alert.risk_level 대신 DDL과 맞춘 alert.situ_state 사용
    print(f"🚨 [위험 감지!] 젯슨 {alert.jetson_id} / 센서 {alert.sen_id} : {alert.situ_state} - {alert.detail}")
    
    # 여기서 나중에 CRUD를 통해 situ_trans 테이블에 기록을 남기는 로직을 추가하면 완벽해!
    # 예: crud.create_situ_record(db, alert)
    
    return {"message": "Alert sent to App successfully", "data": alert}