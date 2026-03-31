from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

# 1. 젯슨 (jetson) 테이블
class Jetson(Base):
    __tablename__ = "jetson"
    jetson_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jetson_wp = Column(String(200), nullable=False)
    jetson_loc = Column(String(200), nullable=False)
    jetson_status = Column(Boolean, nullable=False, default=False) 
    ip_addr = Column(String(45), nullable=False)
    port = Column(SmallInteger, nullable=False)

# 2. 센서 (sensor) 테이블
class Sensor(Base):
    __tablename__ = "sensor"
    sen_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    sensor_type = Column(String(100), nullable=False) 
    sen_name = Column(String(200), nullable=False)    
    sen_locate = Column(String(200), nullable=False)
    mqtt_topic = Column(String(100), nullable=True)
    register_date = Column(Date, nullable=False, default=datetime.utcnow)

# 3. 이벤트 코드 (event_code) 테이블
class EventCode(Base):
    __tablename__ = "event_code"
    ev_code_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ev_code_name = Column(String(50), nullable=False, unique=True)
    ev_code_desc = Column(String(255), nullable=False)

# 4. 작업자 (worker) 테이블
class Worker(Base):
    __tablename__ = "worker"
    dept_id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(200), nullable=False) 
    is_manager = Column(Boolean, nullable=False, default=False)                                
    sen_id = Column(Integer, ForeignKey("sensor.sen_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)   

# 5. 연결_스마트폰 (connect) 테이블
class Connect(Base):
    __tablename__ = "connect"
    connect_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dept_id = Column(Integer, ForeignKey("worker.dept_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    app_id = Column(String(100), nullable=False)

# 6. 관리하다 (manage) 테이블
class Manage(Base):
    __tablename__ = "manage"
    worker_dept_id = Column(Integer, ForeignKey("worker.dept_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    manager_dept_id = Column(Integer, ForeignKey("worker.dept_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

# 7. 온습도 전송 (th_trans) 테이블
class ThTrans(Base):
    __tablename__ = "th_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    temp = Column(Float, nullable=True) 
    humid = Column(Float, nullable=True)

# 8. 심박밴드 전송 (hb_trans) 테이블
class HbTrans(Base):
    __tablename__ = "hb_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    hr = Column(Float, nullable=True)

# 9. 이벤트 (event) 테이블
class Event(Base):
    __tablename__ = "event"
    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ev_code_id = Column(Integer, ForeignKey("event_code.ev_code_id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    sen_id = Column(Integer, ForeignKey("sensor.sen_id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    message = Column(String(255), nullable=False)
    detected_value = Column(String(100), nullable=True)
    time = Column(DateTime, nullable=False, default=datetime.utcnow)

# 10. 카메라 정보 (camera_info) 테이블
class CameraInfo(Base):
    __tablename__ = "camera_info"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    ip_address = Column(String(45), nullable=False)
    camera_id = Column(String(255), nullable=False)  
    camera_pw = Column(String(255), nullable=False)