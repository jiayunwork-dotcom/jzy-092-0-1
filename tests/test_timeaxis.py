"""时间轴离散:覆盖完整穿透过程、均匀布点。"""

import pytest

from app import thomas, timeaxis

PARAMS = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


def test_axis_covers_full_breakthrough():
    times = timeaxis.discretize(**PARAMS)
    assert times[0] == 0.0
    t50 = timeaxis.midpoint_time(**{k: PARAMS[k] for k in ("c0", "flow", "q0", "mass")})
    assert times[-1] > t50
    # 末端已饱和:相对浓度与 1 的差距可忽略
    assert thomas.relative_concentration(times[-1], **PARAMS) > 0.999999


def test_uniform_spacing_and_length():
    points = 101
    times = timeaxis.discretize(**PARAMS, points=points)
    assert len(times) == points
    steps = {round(b - a, 9) for a, b in zip(times, times[1:])}
    assert len(steps) == 1


def test_points_must_be_at_least_two():
    with pytest.raises(ValueError):
        timeaxis.discretize(**PARAMS, points=1)
