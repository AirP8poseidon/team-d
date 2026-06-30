"""멱등 초기화 테스트 (결정 2A) — init+seed 2회 호출 시 행수 동일."""
import db


def _counts():
    conn = db.get_db()
    try:
        tables = ["usage_log", "servers", "posts"]
        return {t: conn.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()["c"] for t in tables}
    finally:
        conn.close()


def test_init_and_seed_idempotent():
    db.init_db()
    db.seed_if_empty()
    first = _counts()

    # 두 번째 호출은 아무것도 추가하지 않아야 한다
    db.init_db()
    db.seed_if_empty()
    second = _counts()

    assert first == second
    # 시드가 실제로 데이터를 넣었는지 (빈 게 아니어야 의미 있음)
    assert all(v > 0 for v in first.values())
