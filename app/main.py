from fastapi import FastAPI
from app.db.database import Base, engine
from app.routers import api_module

# 시작할 때 DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jetson API Calling Module",
    description="관리자 앱 통신 및 젯슨 내부 위험 정보 중계 시스템",
    version="3.0.0",
)

# API 호출 모듈 라우터 연결
app.include_router(api_module.router)

@app.get("/")
def root():
    return {"message": "Jetson API Module is running!"}