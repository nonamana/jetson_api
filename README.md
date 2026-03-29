# 파일 및 함수 역할 정리

## `main.py`
- **함수**
  - 별도 함수 없음
- **역할**
  - 프로그램이 시작되는 메인 파일입니다.
  - 데이터베이스 테이블을 생성하고, 시스템 API, 센서 API, 데이터 조회 API를 FastAPI에 등록합니다.

---

## `database.py`
- **함수**
  - `get_db()`
- **역할**
  - 데이터베이스 연결을 만드는 파일입니다.
  - `engine`, `SessionLocal`, `Base`를 설정하고, `get_db()`는 API가 DB를 사용할 수 있도록 연결을 열고 작업이 끝나면 닫아줍니다.

### `get_db()`
- **역할**
  - 데이터베이스 세션을 꺼내서 API 함수에 전달합니다.
  - 작업이 끝나면 연결을 자동으로 닫습니다.

---

## `models.py`
- **함수**
  - 함수 없음
- **역할**
  - 실제 데이터베이스 테이블 구조를 Python 클래스로 옮겨둔 파일입니다.
  - 센서, 작업자, 작업장, 온습도 데이터, 워치 데이터, 상황 데이터 같은 테이블을 정의합니다.

### `Sensor`
- **역할**
  - 등록된 센서 기본 정보를 저장하는 테이블입니다.
  - 센서 구분, 제조사, 제품명, 제품번호, 관리번호, 작업장 번호를 가집니다.

### `StateCode`
- **역할**
  - 상태 코드 정보를 저장하는 테이블입니다.

### `Worker`
- **역할**
  - 작업자 정보를 저장하는 테이블입니다.
  - 이름, 성별, 나이, 직급, 관리자 여부, 작업장 정보를 가집니다.

### `Manage`
- **역할**
  - 작업자와 관리자의 연결 관계를 저장하는 테이블입니다.

### `ThTrans`
- **역할**
  - 온도와 습도 측정값을 저장하는 테이블입니다.

### `WdTrans`
- **역할**
  - 워치에서 들어온 피부온도와 심박수를 저장하는 테이블입니다.

### `SituTrans`
- **역할**
  - 상황 설명 문자열을 저장하는 테이블입니다.
  - 예를 들어 위험 상황 문장이나 감지 결과를 넣는 용도입니다.

### `EventTrans`
- **역할**
  - 작업자 이벤트 정보를 저장하는 테이블입니다.
  - 상태 코드와 상세 내용을 함께 저장합니다.

### `Workplace`
- **역할**
  - 작업장 기본 정보를 저장하는 테이블입니다.
  - 작업장 번호와 작업장 이름을 관리합니다.

---

## `crud.py`
- **함수**
  - `create_sensor()`
  - `get_sensor_list()`
  - `get_sensor_by_id()`
  - `get_sensor_by_num()`
  - `get_sensors_by_workplace()`
  - `create_th_trans()`
  - `create_wd_trans()`
  - `create_situ_trans()`
  - `get_th_trans_by_workplace()`
  - `get_wd_trans_by_workplace()`
  - `get_situ_trans_by_workplace()`
- **역할**
  - 데이터베이스에 저장하고 조회하는 실제 동작을 모아둔 파일입니다.
  - 센서 등록, 센서 조회, 측정 데이터 저장, 작업장별 데이터 조회를 담당합니다.

### `create_sensor(db, sensor_data)`
- **역할**
  - 새 센서를 `sensor` 테이블에 저장합니다.

### `get_sensor_list(db)`
- **역할**
  - 등록된 전체 센서 목록을 조회합니다.

### `get_sensor_by_id(db, sen_id)`
- **역할**
  - 센서 번호로 센서 1개를 조회합니다.

### `get_sensor_by_num(db, sen_num)`
- **역할**
  - 제품번호로 센서를 조회합니다.
  - 같은 제품번호가 이미 등록됐는지 확인할 때 사용합니다.

### `get_sensors_by_workplace(db, wp_id)`
- **역할**
  - 특정 작업장에 등록된 센서들만 조회합니다.

### `create_th_trans(db, sen_id, wp_id, temp, humd, time)`
- **역할**
  - 온도·습도 측정값을 `th_trans` 테이블에 저장합니다.

### `create_wd_trans(db, sen_id, wp_id, sk_temp, hr, time)`
- **역할**
  - 워치 데이터인 피부온도와 심박수를 `wd_trans` 테이블에 저장합니다.

### `create_situ_trans(db, sen_id, wp_id, detail, time)`
- **역할**
  - 상황 설명 데이터를 `situ_trans` 테이블에 저장합니다.

### `get_th_trans_by_workplace(db, wp_id)`
- **역할**
  - 특정 작업장의 온습도 데이터를 조회합니다.

### `get_wd_trans_by_workplace(db, wp_id)`
- **역할**
  - 특정 작업장의 워치 데이터를 조회합니다.

### `get_situ_trans_by_workplace(db, wp_id)`
- **역할**
  - 특정 작업장의 상황 데이터를 조회합니다.

---

## `system.py`
- **함수**
  - `get_health()`
  - `get_info()`
- **역할**
  - 서버 상태와 Jetson 기본 정보를 알려주는 API 파일입니다.

### `get_health()`
- **역할**
  - 서버가 살아있는지 확인합니다.
  - 현재 시간도 함께 반환합니다.

### `get_info()`
- **역할**
  - Jetson 장치 정보, 호스트 이름, IP, 포트, MQTT 주소, 작업장 이름 등을 반환합니다.

---

## `sensors.py`
- **함수**
  - `start_sensor_discovery()`
  - `stop_sensor_discovery()`
  - `get_sensors_ready()`
  - `create_sensor()`
  - `get_sensor_list()`
  - `get_sensor_list_by_workplace()`
  - `get_sensor_detail()`
- **역할**
  - 센서 탐지, 등록, 조회 API를 처리하는 파일입니다.
  - 앱이 실제로 많이 호출하게 되는 센서 관련 라우터입니다.

### `start_sensor_discovery()`
- **역할**
  - 센서 탐지를 시작 상태로 바꿉니다.

### `stop_sensor_discovery()`
- **역할**
  - 센서 탐지를 중지 상태로 바꿉니다.

### `get_sensors_ready()`
- **역할**
  - 아직 등록 전인 대기 센서 목록을 반환합니다.

### `create_sensor(request, db)`
- **역할**
  - 앱에서 받은 센서 정보를 DB에 등록합니다.
  - 등록 전에 같은 제품번호가 있는지 먼저 확인합니다.

### `get_sensor_list(db)`
- **역할**
  - 등록된 전체 센서 목록을 DB에서 읽어옵니다.

### `get_sensor_list_by_workplace(wp_id, db)`
- **역할**
  - 작업장 번호를 기준으로 센서 목록을 조회합니다.

### `get_sensor_detail(sen_id, db)`
- **역할**
  - 센서 번호를 기준으로 센서 상세 정보를 조회합니다.
  - 없으면 오류를 반환합니다.

---

## `data.py` (라우터 파일)
- **함수**
  - `get_th_data()`
  - `get_wd_data()`
  - `get_situ_data()`
- **역할**
  - 작업장별 센서 측정 데이터를 조회하는 API 파일입니다.

### `get_th_data(wp_id, db)`
- **역할**
  - 해당 작업장의 온도·습도 데이터를 조회합니다.

### `get_wd_data(wp_id, db)`
- **역할**
  - 해당 작업장의 워치 데이터를 조회합니다.
  - 피부온도와 심박수를 가져옵니다.

### `get_situ_data(wp_id, db)`
- **역할**
  - 해당 작업장의 상황 설명 데이터를 조회합니다.

---

## `sensor.py`
- **함수**
  - 함수 없음
- **역할**
  - 센서 관련 요청 형식과 응답 형식을 정리한 파일입니다.
  - Swagger 문서에 보이는 입력 형식도 여기서 정해집니다.

### `DiscoveredSensor`
- **역할**
  - 탐지된 센서 1개의 형식을 정의합니다.
  - 장치 키, 센서 종류, 이름, 제조사, 제품번호, 토픽, 상태를 담습니다.

### `ReadySensorsResponse`
- **역할**
  - 대기 센서 목록 응답 형식을 정의합니다.

### `SensorCreateRequest`
- **역할**
  - 센서 등록 요청 형식을 정의합니다.
  - 센서 구분, 제조사, 제품명, 제품번호, 관리번호, 작업장 번호를 받습니다.

### `SensorResponse`
- **역할**
  - 센서 등록 후 또는 센서 조회 시 반환할 응답 형식을 정의합니다.

---

## `data.py` (스키마 파일)
- **함수**
  - 함수 없음
- **역할**
  - 센서 데이터 조회 결과의 응답 형식을 정하는 파일입니다.

### `ThTransResponse`
- **역할**
  - 온습도 데이터 1건의 응답 형식을 정의합니다.

### `WdTransResponse`
- **역할**
  - 워치 데이터 1건의 응답 형식을 정의합니다.

### `SituTransResponse`
- **역할**
  - 상황 데이터 1건의 응답 형식을 정의합니다.

---

## `discovery_service.py`
- **함수**
  - `start_discovery()`
  - `stop_discovery()`
  - `get_ready_sensors()`
- **역할**
  - MQTT로 찾은 센서 후보들을 임시로 들고 있는 파일입니다.
  - 아직 DB에 등록되기 전의 센서 목록을 관리합니다.

### `start_discovery()`
- **역할**
  - 센서 탐지 동작을 시작 상태로 바꿉니다.

### `stop_discovery()`
- **역할**
  - 센서 탐지 동작을 중지 상태로 바꿉니다.

### `get_ready_sensors()`
- **역할**
  - 현재 발견된 센서 목록을 꺼내서 반환합니다.

---

## `mqtt_service.py`
- **함수**
  - `handle_sensor_message()`
- **역할**
  - MQTT로 들어온 센서 메시지를 읽어서 DB에 저장하는 파일입니다.
  - 메시지 종류에 따라 온습도, 워치, 상황 데이터 테이블로 나누어 저장합니다.

### `handle_sensor_message(topic, payload)`
- **역할**
  - MQTT 메시지를 JSON으로 해석합니다.
  - `type` 값이 `TH`면 온습도 데이터로 저장합니다.
  - `type` 값이 `WD`면 워치 데이터로 저장합니다.
  - `type` 값이 `SITU`면 상황 데이터로 저장합니다.
  - 마지막에는 DB 연결을 닫습니다.

---

## `requirement.txt`
- **함수**
  - 없음
- **역할**
  - 이 프로젝트를 실행할 때 필요한 라이브러리 목록입니다.
  - FastAPI, SQLAlchemy, MQTT, MySQL/Oracle 연결 라이브러리가 들어 있습니다.
