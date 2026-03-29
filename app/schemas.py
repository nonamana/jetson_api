from pydantic import BaseModel
from typing import List, Optional

# 젯슨 등록용
class JetsonCreate(BaseModel):
    jetson_wp: str
    jetson_loc: str
    status: bool = True
    ip_addr: str
    port: int

class JetsonResponse(JetsonCreate):
    jetson_id: int
    class Config:
        from_attributes = True

# 센서 등록용
class SensorCreate(BaseModel):
    sensor_type: str
    sen_name: str
    status: str
    jetson_id: int

class SensorResponse(SensorCreate):
    sen_id: int
    class Config:
        from_attributes = True

# 카메라 등록용
class CameraCreate(BaseModel):
    sensor_type: str = "CAM"
    sen_name: str
    status: str
    jetson_id: int
    ip_address: str
    camera_id: str
    camera_pw: str

# 위험 정보 알림용 (내부 모듈 -> API 서버)
class HazardAlert(BaseModel):
    sen_id: int
    jetson_id: int
    risk_level: str
    detail: str