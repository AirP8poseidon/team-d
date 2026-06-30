"""
팀원1(위키·채팅) 라우터 최소 테스트 공통 설정.

핵심: 라우터는 import 시점에 환경변수 HPC_DB로 DB 경로를 고정하고 init_db()를 돈다.
따라서 라우터 import "이전에" 일회용 임시 DB를 지정해 실제 hpc.db를 절대 건드리지 않는다.
"""
import os
import tempfile

# 라우터 import 전에 임시 DB 경로 지정 (실제 hpc.db 보호)
_TMP_DB = os.path.join(tempfile.mkdtemp(prefix="hpc_test_"), "test.db")
os.environ["HPC_DB"] = _TMP_DB

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers import wiki, chat  # noqa: E402  (env 설정 후 import 의도)


@pytest.fixture(scope="session")
def client():
    app = FastAPI()
    app.include_router(wiki.router)
    app.include_router(chat.router)
    return TestClient(app)
