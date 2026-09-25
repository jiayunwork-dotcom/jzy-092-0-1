"""Thomas 内核:曲线方向、单调性与数值稳定性。"""

import pytest

from app import thomas

PARAMS = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


def test_midpoint_is_half():
    t50 = PARAMS["q0"] * PARAMS["mass"] / (PARAMS["flow"] * PARAMS["c0"])
    assert thomas.relative_concentration(t50, **PARAMS) == pytest.approx(
        0.5, abs=1e-12
    )


def test_curve_climbs_from_low_to_high():
    # 早期远低于进料、晚期逼近进料;指数项符号写反时该测试必挂。
    early = thomas.relative_concentration(0.0, **PARAMS)
    late = thomas.relative_concentration(200.0, **PARAMS)
    assert early < 1e-6
    assert late > 0.999


def test_monotonic_increasing():
    times = [i * 0.5 for i in range(400)]
    ratios = [thomas.relative_concentration(t, **PARAMS) for t in times]
    assert all(b >= a for a, b in zip(ratios, ratios[1:]))


def test_logistic_extreme_values_no_overflow():
    assert thomas.logistic(1000.0) == pytest.approx(0.0, abs=1e-300)
    assert thomas.logistic(-1000.0) == pytest.approx(1.0, abs=1e-15)


def test_concentration_scales_with_c0():
    t = 50.0
    ratio = thomas.relative_concentration(t, **PARAMS)
    assert thomas.concentration(t, **PARAMS) == pytest.approx(
        PARAMS["c0"] * ratio
    )
