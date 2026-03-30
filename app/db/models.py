# DB 테이블을 파이썬 코드로 번역
# DB에 저장되는 원본 테이블 형태

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.db.database import Base

class Jetson(Base):
    __tablename__ = "jetson"
    jetson_id = Column(Integer, primary_key=True, index=True) # AUTO_INCREMENT(자동 증가)
    jetson_wp = Column(String(10))
    jetson_loc = Column(String(20))
    jetson_status = Column(Boolean)
    ip_addr = Column(String(15))
    port = Column(Integer)

class Sensor(Base):
    __tablename__ = "sensor"
    sen_id = Column(Integer, primary_key=True, index=True)
    sensor_type = Column(String(10)) 
    sen_name = Column(String(20))    
    sensor_status = Column(String(20))      
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id"))

class StateCode(Base):
    __tablename__ = "state_code"
    st_cd_id = Column(Integer, primary_key=True, index=True)
    st_sp = Column(String(20))       

class Worker(Base):
    __tablename__ = "worker"
    dept_id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(50))                               
    is_manager = Column(Boolean)                            
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"))   

class Manage(Base):
    __tablename__ = "manage"
    worker_dept_id = Column(Integer, ForeignKey("worker.dept_id"), primary_key=True)
    manager_dept_id = Column(Integer, ForeignKey("worker.dept_id"))

class ThTrans(Base):
    __tablename__ = "th_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id"))
    temp = Column(Float) 
    humd = Column(Float) 

class HbTrans(Base):
    __tablename__ = "hb_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id"))
    hr = Column(Float)   

class SituTrans(Base):
    __tablename__ = "situ_trans"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    time = Column(DateTime, primary_key=True, default=datetime.utcnow)
    jetson_id = Column(Integer, ForeignKey("jetson.jetson_id"))
    situ_state = Column(String(50)) 
    detail = Column(String(200)) 

class CameraInfo(Base):
    __tablename__ = "camera_info"
    sen_id = Column(Integer, ForeignKey("sensor.sen_id"), primary_key=True)
    ip_address = Column(String(15))  
    camera_id = Column(String(255))  
    camera_pw = Column(String(255))