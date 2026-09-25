"""单一工况的完整穿透计算编排:曲线 + 穿透时刻 + 累计吸附量。"""

from __future__ import annotations

from . import breakthrough, integrate, thomas, timeaxis, validation

# 末端相对浓度达到该值才认为床层接近饱和;曲线未越过半程时
# 绝不会满足该条件,服务不会提前宣称饱和。
SATURATION_RATIO = 0.99


def run_case(
    payload: object,
    points: object = None,
    threshold: object = None,
) -> dict:
    """对单一工况完成整条穿透曲线的计算。

    返回曲线(时刻 / 相对浓度 / 出水浓度)、穿透时刻、累计吸附量、
    理论容量与饱和判据。入参不合法时抛出
    :class:`validation.ValidationError`。
    """
    params = validation.validate_case(payload)
    n_points = (
        timeaxis.DEFAULT_POINTS
        if points is None
        else validation.validate_points(points)
    )
    thr = (
        breakthrough.DEFAULT_THRESHOLD
        if threshold is None
        else validation.validate_threshold(threshold)
    )

    times = timeaxis.discretize(**params, points=n_points)
    ratios = thomas.curve(times, **params)
    cumulative = integrate.cumulative_adsorption(
        times, ratios, params["c0"], params["flow"]
    )

    capacity = params["q0"] * params["mass"]
    adsorbed = cumulative[-1]
    return {
        "case": params,
        "threshold": thr,
        "points": n_points,
        "curve": {
            "time": times,
            "ratio": ratios,
            "concentration": [r * params["c0"] for r in ratios],
        },
        "breakthrough_time": breakthrough.crossing_time(times, ratios, thr),
        "cumulative_adsorption": adsorbed,
        "capacity": capacity,
        "saturation_ratio": adsorbed / capacity,
        "saturated": ratios[-1] >= SATURATION_RATIO,
    }
