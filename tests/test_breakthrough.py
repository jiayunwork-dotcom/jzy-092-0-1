"""穿透时刻判定:插值精度与边界情形。"""

import pytest

from app import breakthrough


def test_linear_interpolation_exact():
    times = [0.0, 10.0, 20.0]
    ratios = [0.0, 0.2, 0.4]
    assert breakthrough.crossing_time(times, ratios, 0.1) == pytest.approx(5.0)


def test_never_crosses_returns_none():
    assert breakthrough.crossing_time([0.0, 1.0], [0.01, 0.02], 0.5) is None


def test_already_above_threshold_returns_first_time():
    assert breakthrough.crossing_time([5.0, 6.0], [0.9, 0.95], 0.5) == 5.0


def test_rise_window():
    times = [0.0, 10.0, 20.0, 30.0]
    ratios = [0.0, 0.2, 0.8, 1.0]
    assert breakthrough.rise_window(times, ratios, 0.1, 0.9) == pytest.approx(20.0)
