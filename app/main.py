import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf

from app.db.database import Base, engine
from app.routers import api_module

# 🔍 변경 1: 테이블 생성 로직을 모델들이 다 로드된 뒤에 실행되도록 위치 조정
# (이미 테이블이 생성되어 있다면 무시되니 안심해도 돼)
Base.metadata.create_all(bind=engine)

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
    
    # mDNS 서비스 정보 설정
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