"""pytest 부트스트랩 — 프로젝트 루트를 import 경로에 추가(routers 패키지 임포트용)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
