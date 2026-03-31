# DB 테이블을 파이썬 코드로 번역
# DB에 저장되는 원본 테이블 형태

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


# 1. 젯슨 (jetson) 테이블
class Jetson(Base):
    __tablename__ = "jetson"
    jetson_id = Column(Integer, primary_key=True, index=True)
    jetson_wp = Column(String(200), nullable=False)
    jetson_loc = Column(String(200), nullable=False)
    jetson_status = Column(Boolean, nullable=False) # TINYINT(1)은 Boolean과 매핑됨
    ip_addr = Column(String(15), nullable=False)
    port = Column(Integer, nullable=False)

# 2. 센서 (sensor) 테이블
class Sensor(Base):
    __tablename__ = "sensor"
    sen_id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(String(100), nullable=False) 
    sen_name = Column(String(200), nullable=False)    
    mqtt_topic = Column(String(100), nullable=False)
    register_date = Column(Date, default=datetime.utcnow)

# 3. 상태 (state_code) 테이블
class StateCode(Base):
    __tablename__ = "state_code"
    st_cd_id = Column(Integer, primary_key=True, index=True)
    st_sp = Column(String(20), nullable=False)       

# 4. 작업자 (worker) 테이블
class Worker(Base):
    __tablename__ = "worker"
    dept_id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(200), nullable=False) # DDL 기준 50 -> 200으로 수정
    is_manager = Column(Boolean, nullable=False)                            
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), nullable=False)   

# 5. 관리하다 (manage) 테이블
class Manage(Base):
    __tablename__ = "manage"
    worker_dept_id = Column(Integer, ForeignKey("worker.dept_id"), primary_key=True)
    manager_dept_id = Column(Integer, ForeignKey("worker.dept_id"), nullable=False)

# 6. 온습도 전송 (th_trans) 테이블
class ThTrans(Base):
    __tablename__ = "th_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    # ❌ jetson_id 삭제됨
    temp = Column(Float) 
    humid = Column(Float) # ✏️ humd -> humid 로 이름 변경됨!

# 7. 심박밴드 전송 (hb_trans) 테이블
class HbTrans(Base):
    __tablename__ = "hb_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    # ❌ jetson_id 삭제됨
    hr = Column(Float)

# 8. 상황 전송 (situ_trans) 테이블
class SituTrans(Base):
    __tablename__ = "situ_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow) # 복합키 설정
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id"), nullable=False)
    situ_state = Column(String(100), nullable=False) 
    detail = Column(String(200), nullable=False) 

# 9. 카메라 정보 (camera_info) 테이블
class CameraInfo(Base):
    __tablename__ = "camera_info"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    ip_address = Column(String(15), nullable=False)  
    camera_id = Column(String(255), nullable=False)  
    camera_pw = Column(String(255), nullable=False)