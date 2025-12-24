# 🏭 프로젝트 명세서: PowerPlant-PMS (오프라인 유지보수 통합 플랫폼)

## 1. 프로젝트 개요 (Overview)
* **목표:** 인터넷이 차단된 폐쇄망(Offline) 환경에서 발전소 설비 자산 정보와 유지보수 데이터(점검, 로그)를 통합 관리하는 웹 시스템 구축.
* **핵심 워크플로우:**
    1. **현장(Field):** 업무별(점검/로그)로 분류된 폴더 트리 데이터를 ZIP으로 반출.
    2. **사무실(Office):** 웹 시스템에 ZIP 파일 일괄 업로드.
    3. **시스템(System):** `작업구분 > 설비군 > 자산명 > 날짜_파일명` 구조를 파싱하여 DB 자동화.
* **기술 스택 (Tech Stack):**
    * **Backend:** Python (Django/FastAPI) + **`python-evtx` (로그 파싱 라이브러리)**
    * **Frontend:** React 또는 Vue.js (SPA)
    * **Database:** PostgreSQL (권장 - JSON 데이터 처리에 유리)
    * **Infra:** Docker & Docker Compose (Self-hosted)

---

## 2. 데이터베이스 스키마 설계 (Database Schema)

### 2.1 기초 정보 (Master Data)
* **Systems (설비 계층):** 기능적 분류 (예: 1단계_ECMS, 1단계_GT)
    * `id`, `name`, `parent_id` (Self-FK), `description`
* **Locations (위치 계층):** 물리적 분류 (예: 1block, 전산실)
    * `id`, `name`, `parent_id` (Self-FK), `description`

### 2.2 자산 상세 (Assets Detail)
* **Assets (장비 마스터):**
    * `id` (PK)
    * `system_id` (FK), `location_id` (FK)
    * `asset_tag` (자산번호), **`name` (호스트명/설비명 - Unique Key)**
    * `model`, `manufacturer`, `os_info`
    * `status` (운영/점검/불량)
    * `specs_cpu`, `specs_memory`, `specs_disk` (제원 정보)
* **NetworkInterfaces (네트워크 - 1:N):**
    * `asset_id` (FK), `ip_address`, `mac_address`, `interface_name`
* **Accounts (접속 계정 - 1:N):**
    * `asset_id` (FK), `username`, `password_hash` (**Bcrypt 암호화**), `role`

### 2.3 유지보수 데이터 (Maintenance Data)
* **MaintenanceLogs (점검 이력 - Header):**
    * `id`, `asset_id` (FK)
    * `check_date` (점검일), `check_type` (점검유형 - 예: Disk, Process)
    * `worker` (작업자), `result_status` (Pass/Fail - Event Level 1 발생 시 자동 Fail 처리 가능)
* **MaintenanceDetails (상세 데이터 - Rows):**
    * `log_id` (FK), `item_name` (항목명 - 예: SysLog Level 1 Count), `value` (측정값), `raw_data` (JSON/Text - 상세 내역)
* **LogFiles (증빙 파일):**
    * `log_id` (FK), `file_path` (저장 경로), `file_type` (evtx, txt, conf)

---

## 3. 데이터 파이프라인 및 파싱 규칙 (Data Pipeline Logic)

### 3.1 디렉토리 및 파일명 기반 파싱 (Category-Rooted Structure)
* **업로드 구조:** `[Work_Type]` > `[System_Group]` > `[Asset_Name]` > `[YYMMDD_Filename]`
* **실제 경로 예시:**
    1. `disk,task/1단계_ECMS/1BL_ECMS_EWS1/251209_cpu.txt`
    2. `log,process/1단계_GT_질량유량계(Flow)/1BL_1GT/251210_gt1.txt`
    3. `log,process/1단계_GT_질량유량계(Flow)/1BL_1GT/251210_sys.evtx`

#### (A) 파싱 프로세스 (Step-by-Step)
1.  **Step 1: 작업 유형 식별** (`disk,task` / `log,process`)
2.  **Step 2: 자산 식별** (`Assets.name`으로 ID 매핑)
3.  **Step 3: 파일 처리** (파일명 날짜 추출 및 확장자별 분기 처리)

#### (B) 데이터 적재 로직 (Data Ingestion Rule)

* **Case 1: 성능 데이터 (.txt in `disk,task`)**
    * **로직:** 텍스트 라인 파싱 (Key: Value 추출).
    * **저장:** `MaintenanceDetails`에 항목별 수치 저장.

* **Case 2: 프로세스 현황 데이터 (.txt in `log,process`)**
    * **로직:** 텍스트 전체 읽기 (Full Text Read).
    * **저장:** `MaintenanceDetails`의 `raw_data` 컬럼에 프로세스 목록 전체 텍스트 저장.

* **Case 3: 바이너리 로그 데이터 (.evtx in `log,process`)**
    * **로직:** `python-evtx` 라이브러리를 사용하여 심층 파싱(Deep Parsing).
    * **분석 대상:** `System`, `Application`, `Security` 로그 파일.
    * **필터링 규칙:** `Level` 값이 **1 (Critical), 2 (Error), 3 (Warning)** 인 이벤트만 추출.
    * **집계 (Aggregation):**
        * 각 Level 별로 어떤 `EventID`가 몇 번 발생했는지 카운트.
    * **저장 (Database):**
        * `MaintenanceDetails` 테이블에 요약 정보를 저장한다.
        * **Item Name:** `[File_Type] Event Stats` (예: `sys Event Stats`)
        * **Value:** 위험 이벤트 총 발생 건수 (Level 1+2+3 합계)
        * **Raw Data (JSON):**
          ```json
          {
            "level_1": {"EventID_41": 2, "EventID_1001": 1},
            "level_2": {"EventID_7000": 5},
            "level_3": {"EventID_1014": 12}
          }
          ```
    * **아카이빙:** 원본 `.evtx` 파일은 파일 서버로 이동하고 `LogFiles` 테이블에 링크.

---

## 4. 핵심 기능 요구사항 (Features)

1.  **통합 대시보드:**
    * 설비 계층(Tree) 뷰.
    * **위험 감지:** 전일 업로드된 로그 중 Level 1(Critical)이 포함된 장비 "경고" 표시.
2.  **검색 및 상세 조회:**
    * IP, 자산명, 위치, 날짜별 검색.
    * 상세 페이지 탭 구성: [제원] | [계정] | [점검이력] | [**이벤트로그 분석**]
3.  **보고서 자동화:**
    * 점검 보고서 생성 시, `MaintenanceDetails`에 저장된 **EventID 카운트 정보**를 표 형태로 자동 삽입.
    * 예: *"Sys 로그 분석 결과: Critical 0건, Error 5건 (ID 7000: 5회)"*
4.  **보안 및 관리:**
    * 데이터 변경 이력(Audit Log) 기록.
    * 사용자 권한 관리 및 비밀번호 암호화 저장.

---

## 5. 제약 사항 (Constraints)
* **Network:** 인터넷 차단 환경. `python-evtx` 등 필요한 라이브러리는 사전에 Wheel(.whl) 파일로 준비하여 Docker 이미지에 포함해야 함.
* **Data Source:** 카메라는 사용하지 않으며, 텍스트/로그 파일 기반 데이터 처리.
* **Security:** 비밀번호 등 민감 정보는 DB 내 평문 저장 금지.