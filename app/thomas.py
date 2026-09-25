"""Thomas 解的逐点求值(穿透内核)。

模型固定为:

    C(t)/C0 = 1 / (1 + exp(kTh * (q0*m/Q - C0*t)))

指数项 ``kTh*(q0*m/Q - C0*t)`` 随时间从正变负,相对出水浓度因此从低往高
单调爬升;若把指数项的符号写反,曲线会退化成先高后低的反向形状。这里用
数值稳定的 logistic 实现,并由测试锁住正确的曲线方向。
"""

from __future__ import annotations

import math


def logistic(value: float) -> float:
    """数值稳定的 ``1/(1+exp(value))``,避免指数项过大时溢出。"""
    if value >= 0.0:
        neg = math.exp(-value)
        return neg / (1.0 + neg)
    pos = math.exp(value)
    return 1.0 / (1.0 + pos)


def relative_concentration(
    t: float,
    c0: float,
    flow: float,
    q0: float,
    k_th: float,
    mass: float,
) -> float:
    """时刻 ``t`` 的相对出水浓度 C(t)/C0。"""
    exponent = k_th * (q0 * mass / flow - c0 * t)
    return logistic(exponent)


def concentration(
    t: float,
    c0: float,
    flow: float,
    q0: float,
    k_th: float,
    mass: float,
) -> float:
    """时刻 ``t`` 的出水浓度 C(t)。"""
    return c0 * relative_concentration(t, c0, flow, q0, k_th, mass)


def curve(
    times: list[float],
    c0: float,
    flow: float,
    q0: float,
    k_th: float,
    mass: float,
) -> list[float]:
    """沿给定时间轴逐点求相对出水浓度,返回与时间轴等长的序列。"""
    return [
        relative_concentration(t, c0, flow, q0, k_th, mass) for t in times
    ]
