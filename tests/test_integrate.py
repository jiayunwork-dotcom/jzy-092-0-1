"""亏量积分:梯形法则正确性与容量守恒。"""

import pytest

from app import integrate, thomas, timeaxis

PARAMS = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


def test_trapezoid_constant():
    assert integrate.trapezoid([0.0, 1.0, 2.0], [2.0, 2.0, 2.0]) == pytest.approx(4.0)


def test_trapezoid_linear():
    assert integrate.trapezoid([0.0, 1.0, 2.0], [0.0, 1.0, 2.0]) == pytest.approx(2.0)


def test_trapezoid_length_mismatch():
    with pytest.raises(ValueError):
        integrate.trapezoid([0.0, 1.0], [1.0])


def test_cumulative_adsorption_approaches_capacity():
    """运行足够久,累计吸附量趋近理论容量 q0*m(守恒判据)。"""
    times = timeaxis.discretize(**PARAMS)
    ratios = thomas.curve(times, **PARAMS)
    cumulative = integrate.cumulative_adsorption(
        times, ratios, PARAMS["c0"], PARAMS["flow"]
    )
    capacity = PARAMS["q0"] * PARAMS["mass"]
    assert cumulative[-1] == pytest.approx(capacity, rel=0.01)
    # 累计量单调不减
    assert all(b >= a for a, b in zip(cumulative, cumulative[1:]))
