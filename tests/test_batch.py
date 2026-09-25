"""批量调度:逐条独立求解,中间状态互不累加、互不覆盖。"""

from app import batch, service

CASE_A = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)
CASE_B = dict(c0=80.0, flow=5.0, q0=60.0, k_th=0.01, mass=1500.0)
CASE_C = dict(c0=120.0, flow=20.0, q0=40.0, k_th=0.002, mass=3000.0)
BAD = dict(c0=0.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


def test_batch_matches_individual_runs():
    cases = [CASE_A, CASE_B, CASE_C]
    results = batch.run_batch(cases)
    assert len(results) == len(cases)
    for entry, case in zip(results, cases):
        assert entry["ok"] is True
        assert entry["result"] == service.run_case(case)


def test_batch_isolation_order_independent():
    """同一工况在批量中的结果与其位置、邻接工况无关。"""
    ab = batch.run_batch([CASE_A, CASE_B])
    ba = batch.run_batch([CASE_B, CASE_A])
    assert ab[0]["result"] == ba[1]["result"]
    assert ab[1]["result"] == ba[0]["result"]


def test_invalid_case_does_not_block_others():
    results = batch.run_batch([CASE_A, BAD, CASE_C])
    assert results[0]["ok"] is True
    assert results[1]["ok"] is False
    assert "c0" in results[1]["error"]
    assert results[2]["ok"] is True
    # 失败条目之后的结果仍与单独计算一致
    assert results[2]["result"] == service.run_case(CASE_C)


def test_name_echoed_when_present():
    named = {**CASE_A, "name": "1号床"}
    results = batch.run_batch([named])
    assert results[0]["name"] == "1号床"
