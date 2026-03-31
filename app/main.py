import socket
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from zeroconf import ServiceInfo
from zeroconf.asyncio import AsyncZeroconf

from app.db.database import SessionLocal, engine
from app.db import models, crud
from app.routers.api_module import manager
from app.routers import api_module

# 1. DB 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

def get_real_ip():
    """인터넷 연결이 없는 폐쇄망에서도 현재 할당된 진짜 로컬 IP를 찾아옵니다."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 실제 패킷은 안 나가고 인터페이스만 확인 (10.대역 권장)
        s.connect(('10.255.255.255', 1)) 
        IP = s.getsockname()[0]
    except Exception:
        try:
            IP = socket.gethostbyname(socket.gethostname())
        except:
            IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def startup_db_init(ip: str):
    """서버 부팅 시 현재 IP로 젯슨 테이블 정보를 갱신합니다."""
    db = SessionLocal()
    try:
        jetson_info = {
            "jetson_wp": "제1공장",
            "jetson_loc": "컨베이어 벨트 앞",
            "jetson_status": True,
            "ip_addr": ip,
            "port": 8000
        }
        crud.init_jetson_info(db, jetson_info)
        print(f"✅ [DB] 젯슨 정보 업데이트 완료! IP: {ip}")
    finally:
        db.close()

# 전역 mDNS 객체
aiozc = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 부팅 시 IP 확인, DB 초기화, mDNS 등록을 한꺼번에 처리합니다."""
    global aiozc
    current_ip = get_real_ip()
    
    # 1. DB 초기화
    startup_db_init(current_ip)
    
    # 2. mDNS 서비스 등록 (스마트폰 앱 자동 감지용)
    info = ServiceInfo(
        "_jetsonhub._tcp.local.",
        "DS_Safer_Jetson._jetsonhub._tcp.local.", # 앱에서 찾을 이름
        addresses=[socket.inet_aton(current_ip)],
        port=8000,
        properties={'desc': 'Industrial Safety Monitoring System'}
    )
    
    aiozc = AsyncZeroconf()
    await aiozc.async_register_service(info)
    print(f"📢 [mDNS] 젯슨 방송 시작! (IP: {current_ip}, Port: 8000)")
    
    yield  # 서버 가동 중...
    
    # [SHUTDOWN] 종료 시 mDNS 등록 해제
    if aiozc:
        await aiozc.async_unregister_service(info)
        await aiozc.async_close()
        print("🔇 [mDNS] 젯슨 방송 종료 및 서버 종료")

app = FastAPI(
    title="Industrial Safety API Server",
    description="산업 안전 모듈 데이터 중계 및 관리 시스템 (Integrated mDNS & IP Sync)",
    version="3.3.0",
    lifespan=lifespan
)

# API 라우터 포함
app.include_router(api_module.router)

# 실시간 웹소켓 엔드포인트
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """관리자 스마트폰과 연결을 맺고 세션을 유지합니다."""
    await manager.connect(websocket)
    print(f"🔗 [웹소켓] 새 기기 연결됨 (현재 연결 수: {len(manager.active_connections)})")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"📱 [앱 응답]: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("🔌 [웹소켓] 기기 연결 종료")

@app.get("/")
def root():
    return {
        "status": "online",
        "ip_addr": get_real_ip(),
        "project": "Industrial Safety Monitoring"
    }