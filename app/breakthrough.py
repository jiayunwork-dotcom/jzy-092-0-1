"""穿透时刻判定与爬升窗。"""

from __future__ import annotations

DEFAULT_THRESHOLD = 0.1


def crossing_time(
    times: list[float],
    ratios: list[float],
    threshold: float = DEFAULT_THRESHOLD,
) -> float | None:
    """相对浓度首次达到 ``threshold`` 的时刻,相邻采样点间线性插值。

    曲线单调爬升,首次穿越即唯一穿越;整条曲线始终低于阈值时返回
    ``None``。
    """
    if not times:
        return None
    if ratios[0] >= threshold:
        return times[0]
    for i in range(1, len(times)):
        if ratios[i] >= threshold:
            r0, r1 = ratios[i - 1], ratios[i]
            t0, t1 = times[i - 1], times[i]
            frac = (threshold - r0) / (r1 - r0)
            return t0 + frac * (t1 - t0)
    return None


def rise_window(
    times: list[float],
    ratios: list[float],
    low: float = 0.1,
    high: float = 0.9,
) -> float | None:
    """相对浓度从 ``low`` 爬到 ``high`` 的时间窗,刻画曲线陡峭程度。"""
    t_low = crossing_time(times, ratios, low)
    t_high = crossing_time(times, ratios, high)
    if t_low is None or t_high is None:
        return None
    return t_high - t_low
