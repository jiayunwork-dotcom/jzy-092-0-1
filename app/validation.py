"""工况入参校验:所有工况参数必须为正的有限数值。"""

from __future__ import annotations

import math

FIELDS = ("c0", "flow", "q0", "k_th", "mass")

MAX_POINTS = 100000


class ValidationError(ValueError):
    """携带具体原因的工况校验错误。"""


def validate_case(payload: object) -> dict[str, float]:
    """校验并规范化单一工况,返回标准化参数字典。

    任何字段缺失、非数值、非有限或不为正,都抛出带原因的
    :class:`ValidationError`;额外字段(如 name、points)原样忽略。
    """
    if not isinstance(payload, dict):
        raise ValidationError(f"工况必须是 JSON 对象,收到: {payload!r}")
    params: dict[str, float] = {}
    for field in FIELDS:
        if field not in payload:
            raise ValidationError(f"缺少参数: {field}")
        value = payload[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(f"参数 {field} 必须是数值,收到: {value!r}")
        value = float(value)
        if not math.isfinite(value):
            raise ValidationError(f"参数 {field} 必须是有限数值,收到: {value!r}")
        if value <= 0.0:
            raise ValidationError(f"参数 {field} 必须为正数,收到: {value}")
        params[field] = value
    return params


def validate_points(value: object) -> int:
    """校验采样点数:整数且在 [2, MAX_POINTS] 内。"""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"points 必须是整数,收到: {value!r}")
    if value < 2 or value > MAX_POINTS:
        raise ValidationError(f"points 必须在 2..{MAX_POINTS} 之间,收到: {value}")
    return value


def validate_threshold(value: object) -> float:
    """校验穿透阈值:开区间 (0, 1) 内的数值。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"threshold 必须是数值,收到: {value!r}")
    value = float(value)
    if not math.isfinite(value) or not 0.0 < value < 1.0:
        raise ValidationError(f"threshold 必须在 (0, 1) 区间内,收到: {value!r}")
    return value
