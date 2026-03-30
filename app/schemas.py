# 스마트폰에서 받은 JSON 데이터가 규격에 맞는지 검사
# app/models.py에는 DB 구조가 존재하고, schemas.py에는 통신 규격이 존재하는 것

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# --- 1. 젯슨 (Jetson) 관련 규격 ---
class JetsonCreate(BaseModel):
    jetson_wp: str
    jetson_loc: str
    jetson_status: bool = True
    ip_addr: str
    port: int

class JetsonResponse(JetsonCreate):
    jetson_id: int
    
    model_config = ConfigDict(from_attributes=True) # Pydantic v2 방식

# --- 2. 센서 (Sensor) 관련 규격 ---
class SensorCreate(BaseModel):
    sensor_type: str
    sen_name: str
    sen_status: bool = True # sensor_status에서 sen_status로 수정 (DDL 일치)
    jetson_id: int

class SensorResponse(SensorCreate):
    sen_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- 3. 카메라 (Camera) 관련 규격 ---
# 카메라 정보는 DB상에서 'sensor'와 'camera_info' 두 군데에 나눠서 저장되므로
# 등록할 때는 모든 정보를 한 번에 받도록 구성합니다.
class CameraCreate(BaseModel):
    # sensor 테이블용
    sensor_type: str = "CAM"
    sen_name: str
    sen_status: bool = True # DDL 일치
    jetson_id: int
    # camera_info 테이블용
    ip_address: str
    camera_id: str
    camera_pw: str

# --- 4. 데이터 전송용 (Trans) 관련 규격 ---
# 위험 정보 알림 (situ_trans 테이블 기반)
class HazardAlert(BaseModel):
    sen_id: int
    jetson_id: int
    situ_state: str # risk_level에서 situ_state로 수정 (DDL 일치)
    detail: str
    # time은 서버에서 생성하거나 선택적으로 받을 수 있음
    time: Optional[datetime] = None

# 온습도 전송용 (th_trans)
class ThTransCreate(BaseModel):
    sen_id: int
    jetson_id: int
    temp: float
    humd: float

# 심박수 전송용 (hb_trans)
class HbTransCreate(BaseModel):
    sen_id: int
    jetson_id: int
    hr: float