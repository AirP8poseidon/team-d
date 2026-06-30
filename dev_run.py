"""
dev_run.py — 팀원1(위키·채팅) 단독 실행용 개발 하네스

목적: 팀장 main.py 없이도 내 파트를 혼자 띄워 /docs 단독 응답 + 화면을 검증한다.
통합 시에는 팀장 main.py 가 이 파일을 대체한다(이 파일은 통합 산출물이 아님).

실행:
    pip install fastapi "uvicorn[standard]"
    uvicorn dev_run:app --reload --port 8000
    # 위키 화면:  http://localhost:8000/        (→ /static/wiki.html)
    # API 문서:   http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from routers import wiki, chat

app = FastAPI(title="HPC 포털 — 팀원1(위키·채팅) 단독 실행")
app.include_router(wiki.router)
app.include_router(chat.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/wiki.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
