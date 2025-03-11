# 한국 판례 검색 API

법제처 사이트에서 제공하는 판례 정보를 검색하고 조회할 수 있는 FastAPI 기반 REST API입니다.

## 기능

- 판례 목록 검색
- 판례 상세 내용 조회
- 원본 형식 그대로의 API 결과 반환

## 설치 및 실행

### 요구사항

- Python 3.8 이상

### 설치

1. 저장소를 클론합니다.
```bash
git clone [저장소 URL]
cd korean-cases-api
```

2. 가상 환경을 생성하고 활성화합니다.
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 필요한 패키지를 설치합니다.
```bash
pip install -r requirements.txt
```

4. (선택사항) `.env` 파일을 생성하여 API 키를 설정합니다.
```
LAW_API_OC=your_api_key_here
```

### 실행

```bash
uvicorn main:app --reload
```

서버가 실행되면 `http://localhost:8000`에서 API에 접근할 수 있습니다.
API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## API 엔드포인트

### GET /api/cases

판례 목록을 검색합니다.

**쿼리 파라미터:**
- `query`: 검색어
- `search`: 검색범위 (1: 판례명, 2: 본문검색)
- `display`: 검색 결과 개수 (최대 100)
- `page`: 검색 결과 페이지
- 기타 다양한 검색 조건

### GET /api/cases/{case_id}

특정 판례의 상세 내용을 조회합니다.

**경로 파라미터:**
- `case_id`: 판례 일련번호

**쿼리 파라미터:**
- `type`: 출력 형태 (HTML)

### GET /api/cases/raw

판례 검색 결과를 원본 형식 그대로 반환합니다.

**쿼리 파라미터:**
- `query`: 검색어
- `output_type`: 출력 형태 (HTML/XML/JSON)

## 참고사항

이 API는 법제처에서 제공하는 판례 데이터를 활용합니다. 자세한 내용은 법제처 사이트를 참조하세요. 