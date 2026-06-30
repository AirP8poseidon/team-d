"""pytest 공통 픽스처 — 임시 DB 로 app.db 를 건드리지 않는다.

HPC_DB_PATH 환경변수를 임시 파일로 지정한 뒤 db 모듈을 import 하므로
DB_PATH 가 임시 경로로 잡힌다. sys.path 에 hpc-portal 루트를 추가한다.
"""
import os
import sys
import tempfile

import pytest

# hpc-portal 루트를 import 경로에 추가 (db, main, routers, collectors)
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


@pytest.fixture(scope="session", autouse=True)
def _temp_db():
    """세션 전체에 임시 DB 경로를 강제."""
    fd, path = tempfile.mkstemp(suffix="_test.db")
    os.close(fd)
    os.environ["HPC_DB_PATH"] = path

    import db
    db.DB_PATH = path  # 이미 import 됐을 수 있으니 모듈 변수도 갱신

    yield path

    for p in (path, path + "-wal", path + "-shm"):
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass
