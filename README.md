# 🏭 PowerPlant-PMS (오프라인 유지보수 통합 플랫폼)

발전소 설비 자산 정보와 유지보수 데이터를 통합 관리하는 웹 시스템입니다.

## 📋 프로젝트 개요

- **목적**: 인터넷이 차단된 폐쇄망 환경에서 발전소 설비 유지보수 데이터 관리
- **기술 스택**:
  - Backend: FastAPI (Python)
  - Frontend: React (Material-UI)
  - Database: PostgreSQL
  - Infrastructure: Docker & Docker Compose

## 🚀 빠른 시작

### 사전 요구사항

- Docker & Docker Compose
- (선택) Python 3.11+, Node.js 18+ (로컬 개발용)

### 실행 방법

1. **프로젝트 클론**
```bash
git clone <repository-url>
cd server
```

2. **환경 변수 설정** (선택사항)
```bash
cp .env.example .env
# .env 파일 수정
```

3. **Docker Compose로 실행**
```bash
docker-compose up -d
```

4. **접속**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API 문서: http://localhost:8000/docs

## 📁 프로젝트 구조

```
server/
├── backend/              # FastAPI 백엔드
│   ├── app/
│   │   ├── api/         # API 라우터
│   │   ├── models/      # SQLAlchemy 모델
│   │   ├── schemas/     # Pydantic 스키마
│   │   ├── services/    # 비즈니스 로직
│   │   └── core/        # 설정 및 데이터베이스
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React 프론트엔드
│   ├── src/
│   │   ├── components/  # React 컴포넌트
│   │   ├── pages/       # 페이지 컴포넌트
│   │   └── services/    # API 서비스
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 주요 기능

1. **ZIP 파일 업로드 및 자동 파싱**
   - 디렉토리 구조 기반 자동 분류
   - 텍스트 파일 및 EVTX 로그 파일 처리

2. **자산 관리**
   - 설비 계층 구조 관리
   - 자산 정보 조회 및 검색

3. **점검 이력 관리**
   - 점검 데이터 자동 저장
   - 이벤트 로그 분석 (Level 1/2/3 필터링)

4. **대시보드**
   - 통계 정보 표시
   - 위험 감지 알림

## 📝 데이터 파싱 규칙

### 업로드 구조
```
[Work_Type] > [System_Group] > [Asset_Name] > [YYMMDD_Filename]
```

예시:
- `disk,task/1단계_ECMS/1BL_ECMS_EWS1/251209_cpu.txt`
- `log,process/1단계_GT/1BL_1GT/251210_sys.evtx`

### 파일 처리
- **.txt (disk,task)**: Key:Value 형태 파싱
- **.txt (log,process)**: 전체 텍스트 저장
- **.evtx**: python-evtx로 이벤트 로그 분석 (Level 1/2/3만 추출)

## 🔒 보안

- 비밀번호는 Bcrypt로 암호화 저장
- 민감 정보 평문 저장 금지
- 오프라인 환경 대응 (필요 라이브러리 사전 포함)

## 📚 API 문서

실행 후 http://localhost:8000/docs 에서 Swagger UI로 API 문서를 확인할 수 있습니다.

## 🛠️ 개발

### 백엔드 로컬 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 프론트엔드 로컬 실행
```bash
cd frontend
npm install
npm start
```

## 📄 라이선스

이 프로젝트는 내부 사용을 위한 것입니다.

