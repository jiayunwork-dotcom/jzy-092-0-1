"""关键参数规律:容量加倍推后穿透、流量加倍提前穿透、
速率常数增大曲线变陡、进料浓度为零报错、累计吸附守恒。"""

import pytest

from app import service, validation
from app.breakthrough import rise_window

BASE = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


def _run(**overrides):
    return service.run_case({**BASE, **overrides})


def _window(result):
    return rise_window(
        result["curve"]["time"], result["curve"]["ratio"], 0.1, 0.9
    )


def test_capacity_doubling_delays_breakthrough_twofold():
    """单位吸附容量加倍、其余不变,穿透时刻大致推后一倍。"""
    base = _run()
    doubled = _run(q0=BASE["q0"] * 2.0)
    ratio = doubled["breakthrough_time"] / base["breakthrough_time"]
    assert ratio == pytest.approx(2.0, abs=0.1)


def test_flow_doubling_advances_breakthrough():
    """体积流量加倍,穿透提前到来。"""
    base = _run()
    doubled = _run(flow=BASE["flow"] * 2.0)
    assert doubled["breakthrough_time"] < base["breakthrough_time"]
    ratio = doubled["breakthrough_time"] / base["breakthrough_time"]
    assert 0.3 < ratio < 0.7


def test_larger_rate_constant_steepens_curve():
    """速率常数调大,一成到九成的爬升窗收窄、曲线变陡。"""
    base = _run()
    fast = _run(k_th=BASE["k_th"] * 2.0)
    w_base = _window(base)
    w_fast = _window(fast)
    assert w_fast < w_base
    assert w_fast == pytest.approx(w_base / 2.0, rel=0.05)


def test_zero_feed_concentration_rejected():
    with pytest.raises(validation.ValidationError, match="c0"):
        _run(c0=0.0)


def test_cumulative_adsorption_conserves_capacity():
    """运行足够久,累计吸附量趋近理论容量 q0*m。"""
    result = _run()
    assert result["saturated"] is True
    assert result["cumulative_adsorption"] == pytest.approx(
        result["capacity"], rel=0.01
    )
    assert result["saturation_ratio"] == pytest.approx(1.0, rel=0.01)


def test_curve_shape_low_to_high():
    """曲线从低往高单调爬升,不出现先高后低的反向形状。"""
    result = _run()
    ratios = result["curve"]["ratio"]
    assert ratios[0] < 1e-6
    assert ratios[-1] > 0.999
    assert all(b >= a for a, b in zip(ratios, ratios[1:]))
