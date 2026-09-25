"""HTTP 接口层:单工况、批量、参考算例与错误返回。"""

import pytest

from app.api import create_app

BASE = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_single_case_ok(client):
    resp = client.post("/api/v1/breakthrough", json=BASE)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["breakthrough_time"] is not None
    assert body["cumulative_adsorption"] == pytest.approx(
        body["capacity"], rel=0.01
    )
    ratios = body["curve"]["ratio"]
    assert len(ratios) == len(body["curve"]["time"]) == body["points"]
    assert all(b >= a for a, b in zip(ratios, ratios[1:]))


def test_single_case_zero_c0_returns_400_with_reason(client):
    resp = client.post("/api/v1/breakthrough", json={**BASE, "c0": 0.0})
    assert resp.status_code == 400
    assert "c0" in resp.get_json()["error"]


def test_single_case_rejects_non_json(client):
    resp = client.post("/api/v1/breakthrough", data="not json")
    assert resp.status_code == 400


def test_single_case_points_override(client):
    resp = client.post("/api/v1/breakthrough", json={**BASE, "points": 64})
    assert resp.status_code == 200
    assert len(resp.get_json()["curve"]["time"]) == 64


def test_batch_endpoint(client):
    other = {**BASE, "flow": 20.0}
    resp = client.post(
        "/api/v1/breakthrough/batch", json={"cases": [BASE, other]}
    )
    assert resp.status_code == 200
    results = resp.get_json()["results"]
    assert [r["ok"] for r in results] == [True, True]
    # 流量大的工况穿透更早
    assert (
        results[1]["result"]["breakthrough_time"]
        < results[0]["result"]["breakthrough_time"]
    )


def test_batch_endpoint_requires_cases_array(client):
    resp = client.post("/api/v1/breakthrough/batch", json={"cases": {}})
    assert resp.status_code == 400


def test_reference_case_pre_breakthrough_effluent_far_below_feed(client):
    """参考算例:穿透发生之前出水浓度远低于进料浓度。"""
    ref = client.get("/api/v1/reference-case").get_json()
    resp = client.post("/api/v1/breakthrough", json=ref)
    assert resp.status_code == 200
    body = resp.get_json()
    t_b = body["breakthrough_time"]
    times = body["curve"]["time"]
    ratios = body["curve"]["ratio"]
    pre = [r for t, r in zip(times, ratios) if t <= 0.5 * t_b]
    assert pre and max(pre) < 0.01
