import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf

from app.db.database import SessionLocal, engine
from app.db import models, crud
from app.routers import api_module

# 🔍 변경 1: 테이블 생성 로직을 모델들이 다 로드된 뒤에 실행되도록 위치 조정
models.Base.metadata.create_all(bind=engine)

# 2. 내 IP 찾기
def get_real_ip():
    """외부와 통신할 때 사용하는 진짜 로컬 IP를 가져옵니다."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 실제로 연결하지는 않고, 외부로 나가는 길목(인터페이스)만 확인합니다.
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# 3. 서버 부팅 시 하드코딩된 젯슨 정보 밀어넣기
def startup_db_init():
    db = SessionLocal()
    try:
        # 💡 여기에 기원님이 원하는 젯슨 초기값을 하드코딩합니다!
        current_ip = get_real_ip()

        hardcoded_info = {
            "jetson_id": 1,
            "jetson_wp": "제1공장",
            "jetson_loc": "컨베이어 벨트 앞",
            "jetson_status": True,
            "ip_addr": current_ip,
            "port": 8000
        }
        crud.init_jetson_info(db, hardcoded_info)
        print(f"✅ 젯슨 초기 정보 DB 세팅 완료! (IP: {current_ip})")
    finally:
        db.close()

# 함수 실행!
startup_db_init()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

aiozc = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global aiozc
    ip = get_ip_address()
    
    # mDNS 서비스 정보 설정 / 와이파이에 젯슨 본인의 정보를 알리는 역할
    info = ServiceInfo(
        "_jetsonhub._tcp.local.",
        "DS_Safer_Jetson._jetsonhub._tcp.local.",
        addresses=[socket.inet_aton(ip)],
        port=8000,
        properties={'desc': 'Industrial Safety Monitoring System'} # 설명 업데이트
    )
    
    aiozc = AsyncZeroconf()
    await aiozc.async_register_service(info)
    print(f"📢 [mDNS] 젯슨 방송 시작! IP: {ip}, Port: 8000")
    
    yield 
    
    if aiozc:
        await aiozc.async_unregister_service(info)
        await aiozc.async_close()
        print("🔇 [mDNS] 젯슨 방송 종료")

app = FastAPI(
    title="Industrial Safety API Server", # 제목을 프로젝트 주제에 맞게 변경
    description="산업 안전 모듈 데이터 중계 및 관리 시스템 (Update: DDL Sync)",
    version="3.1.0", # 규격 업데이트에 맞춰 버전 업!
    lifespan=lifespan
)

app.include_router(api_module.router)

@app.get("/")
def root():
    # 🔍 변경 2: 루트 접속 시 서버 상태를 좀 더 명확히 보여주면 좋음
    return {
        "status": "online",
        "project": "Industrial Safety Monitoring",
        "message": "Jetson API Module is running with latest DDL schema!"
    }