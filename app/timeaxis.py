"""时间轴离散。

终点取在指数项已充分为负的位置:中点(C/C0 = 0.5)之后再留出
``TAIL_MARGIN`` 个单位的指数裕量,保证末端 C/C0 与 1 的差距可忽略、
床层接近饱和,亏量积分才能收敛到理论容量 q0*m。
"""

from __future__ import annotations

DEFAULT_POINTS = 400
TAIL_MARGIN = 20.0


def midpoint_time(c0: float, flow: float, q0: float, mass: float) -> float:
    """指数项为零(C/C0 = 0.5)对应的时刻。"""
    return q0 * mass / (flow * c0)


def end_time(
    c0: float,
    flow: float,
    q0: float,
    k_th: float,
    mass: float,
    margin: float = TAIL_MARGIN,
) -> float:
    """时间轴终点:中点之后再加 ``margin/(kTh*C0)`` 的饱和裕量。"""
    return midpoint_time(c0, flow, q0, mass) + margin / (k_th * c0)


def discretize(
    c0: float,
    flow: float,
    q0: float,
    k_th: float,
    mass: float,
    points: int = DEFAULT_POINTS,
    start: float = 0.0,
    margin: float = TAIL_MARGIN,
) -> list[float]:
    """生成 ``points`` 个均匀分布的时刻,从 ``start`` 到 :func:`end_time`。"""
    if points < 2:
        raise ValueError(f"采样点数必须 >= 2,收到: {points}")
    end = end_time(c0, flow, q0, k_th, mass, margin=margin)
    step = (end - start) / (points - 1)
    return [start + i * step for i in range(points)]
