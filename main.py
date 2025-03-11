from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
import httpx
from typing import Optional, List, Dict, Any
import xmltodict
import os
from dotenv import load_dotenv
import json

# 환경 변수 로드
load_dotenv()

# 기본 API 설정
BASE_URL = "http://www.law.go.kr/DRF"
OC = os.getenv("LAW_API_OC", "test")  # 환경 변수가 없으면 test 사용

app = FastAPI(
    title="한국 판례 검색 API",
    description="법제처 사이트에서 제공하는 판례 정보를 검색하고 조회하는 API입니다.",
    version="1.0.0"
)

# 비동기 HTTP 클라이언트
async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

@app.get("/")
async def root():
    return {"message": "한국 판례 검색 API에 오신 것을 환영합니다. /docs에서 API 문서를 확인하세요."}

@app.get("/api/cases", response_class=JSONResponse)
async def search_cases(
    client: httpx.AsyncClient = Depends(get_http_client),
    query: Optional[str] = Query(None, description="검색어"),
    search: Optional[int] = Query(1, description="검색범위 (1: 판례명, 2: 본문검색)"),
    display: Optional[int] = Query(20, description="검색 결과 개수 (최대 100)"),
    page: Optional[int] = Query(1, description="검색 결과 페이지"),
    org: Optional[str] = Query(None, description="법원종류 (대법원:400201, 하위법원:400202)"),
    curt: Optional[str] = Query(None, description="법원명 (대법원, 서울고등법원 등)"),
    jo: Optional[str] = Query(None, description="참조법령명 (형법, 민법 등)"),
    gana: Optional[str] = Query(None, description="사전식 검색(ga,na,da 등)"),
    sort: Optional[str] = Query(None, description="정렬 옵션"),
    date: Optional[int] = Query(None, description="판례 선고일자"),
    prnc_yd: Optional[str] = Query(None, description="선고일자 검색 (예: 20090101~20090130)"),
    nb: Optional[int] = Query(None, description="판례 사건번호"),
    dat_src_nm: Optional[str] = Query(None, description="데이터출처명")
):
    """
    판례 목록을 검색합니다.
    """
    # API 요청 파라미터 구성
    params = {
        "OC": OC,
        "target": "prec",
        "type": "XML",
        "mobileYn": "Y",
        "display": min(display, 100),  # 최대 100개로 제한
        "page": page,
    }
    
    # 선택적 파라미터 추가
    if query:
        params["query"] = query
    if search:
        params["search"] = search
    if org:
        params["org"] = org
    if curt:
        params["curt"] = curt
    if jo:
        params["JO"] = jo
    if gana:
        params["gana"] = gana
    if sort:
        params["sort"] = sort
    if date:
        params["date"] = date
    if prnc_yd:
        params["prncYd"] = prnc_yd
    if nb:
        params["nb"] = nb
    if dat_src_nm:
        params["datSrcNm"] = dat_src_nm
    
    try:
        # 법제처 API에 요청
        response = await client.get(f"{BASE_URL}/lawSearch.do", params=params)
        response.raise_for_status()
        
        # XML 응답을 파싱
        data = xmltodict.parse(response.text)
        
        # 결과 반환
        return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"외부 API 요청 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/api/cases/{case_id}", response_class=JSONResponse)
async def get_case_detail(
    case_id: int,
    client: httpx.AsyncClient = Depends(get_http_client),
    type: str = Query("HTML", description="출력 형태 (HTML)")
):
    """
    특정 판례의 상세 내용을 조회합니다.
    """
    # API 요청 파라미터 구성
    params = {
        "OC": OC,
        "target": "prec",
        "ID": case_id,
        "type": type,
        "mobileYn": "Y"
    }
    
    try:
        # 법제처 API에 요청
        response = await client.get(f"{BASE_URL}/lawService.do", params=params)
        response.raise_for_status()
        
        # 응답 타입에 따라 처리
        if type.upper() == "HTML":
            return HTMLResponse(content=response.text, status_code=200)
        else:
            # XML을 파싱하여 JSON으로 반환
            data = xmltodict.parse(response.text)
            return data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"외부 API 요청 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/api/cases/raw", response_class=JSONResponse)
async def search_cases_raw(
    client: httpx.AsyncClient = Depends(get_http_client),
    query: Optional[str] = Query(None, description="검색어"),
    output_type: str = Query("XML", description="출력 형태 (HTML/XML/JSON)")
):
    """
    판례 검색 결과를 원본 형식 그대로 반환합니다.
    """
    # API 요청 파라미터 구성
    params = {
        "OC": OC,
        "target": "prec",
        "type": output_type,
        "mobileYn": "Y"
    }
    
    # 검색어가 있는 경우 추가
    if query:
        params["query"] = query
    
    try:
        # 법제처 API에 요청
        response = await client.get(f"{BASE_URL}/lawSearch.do", params=params)
        response.raise_for_status()
        
        # 출력 타입에 따라 응답 처리
        if output_type.upper() == "HTML":
            return HTMLResponse(content=response.text, status_code=200)
        elif output_type.upper() == "JSON":
            return json.loads(response.text)
        else:  # XML
            return {"xml_content": response.text}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"외부 API 요청 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 