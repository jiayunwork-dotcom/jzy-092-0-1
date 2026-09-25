"""浓度亏量沿时间的数值积分(梯形法则,仅标准库)。"""

from __future__ import annotations


def trapezoid(xs: list[float], ys: list[float]) -> float:
    """梯形法则求 ``ys`` 沿 ``xs`` 的定积分。"""
    if len(xs) != len(ys):
        raise ValueError("xs 与 ys 长度必须一致")
    total = 0.0
    for i in range(1, len(xs)):
        total += 0.5 * (ys[i - 1] + ys[i]) * (xs[i] - xs[i - 1])
    return total


def cumulative_adsorption(
    times: list[float],
    ratios: list[float],
    c0: float,
    flow: float,
) -> list[float]:
    """累计吸附量序列 M(t) = Q*C0 * ∫0..t (1 - C/C0) dt。

    逐段梯形积分,返回与时间轴等长的累计序列;运行足够久、床层接近
    饱和时,末值趋近理论容量 q0*m。
    """
    if len(times) != len(ratios):
        raise ValueError("times 与 ratios 长度必须一致")
    cumulative = [0.0]
    for i in range(1, len(times)):
        dt = times[i] - times[i - 1]
        deficit_prev = 1.0 - ratios[i - 1]
        deficit_curr = 1.0 - ratios[i]
        segment = flow * c0 * 0.5 * (deficit_prev + deficit_curr) * dt
        cumulative.append(cumulative[-1] + segment)
    return cumulative
