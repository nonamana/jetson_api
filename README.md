서버 on: python -m uvicorn app.main:app --host 0.0.0.0 --reload
포트 설정할 땐 뒤에 --port 8080, 기본은 8000

API 서버 주소: http://127.0.0.1:8000
테스트(Swagger) 문서: http://127.0.0.1:8000/docs

DB 접속: mysql -u root -p

API 호출 모듈 명세서

1. 젯슨 장비 및 앱 연동

POST /api/jetson/register
기능: 젯슨 장비 등록 및 앱 연동
설명: 관리자 앱에서 사번과 앱 ID를 전송하면, 내부 DB에 연결 정보를 기록하고 젯슨 접속(API/WebSocket) 정보를 반환합니다.

2. 센서 관리

GET /api/sensors/discovered
기능: mDNS 감지 센서 목록 조회
설명: 주변 네트워크에서 감지된 센서 목록(현재 임시 데이터)을 앱에 전달합니다.

POST /api/sensors/register
기능: 센서 다중 등록
설명: 앱에서 선택한 여러 개의 센서(손목밴드, 온습도계 등)를 DB에 일괄 저장합니다.

GET /api/sensors
기능: 등록된 일반 센서 목록 조회
설명: 앱에서 센서 목록 탭을 열 때 호출되며, 전체 센서 중 카메라를 제외한 일반 센서 목록만 반환합니다.

3. 카메라(CCTV) 관리

POST /api/cameras/register
기능: 카메라 등록 및 VLM 중계
설명: 앱에서 입력한 카메라 IP를 기반으로 DB에 저장 및 중복을 검사하고, VLM 서버 연결용 페이로드를 생성합니다.

GET /api/cameras
기능: CCTV 목록 조회
설명: 센서 테이블과 카메라 테이블을 조인하여, 앱 화면에 필요한 카메라 이름, 위치, 상태 정보를 반환합니다.

4. 내부 모듈 중계 (위험 분석)

POST /api/internal/vlm-analysis
기능: 위험 감지 데이터 안전 감지 모듈로 전달 (포워딩)
설명: VLM(카메라 제어 모듈)이 보낸 위험 감지 데이터를 받아, 백그라운드 작업을 통해 '안전 감지 모듈'로 즉시 토스합니다. 병목을 막기 위해 VLM에게는 200 OK만 즉각 반환합니다.