"""预置的软化床参考工况。

单位约定(自洽即可):C0 取 mg/L,Q 取 L/min,q0 取 mg/g,m 取 g,
kTh 取 L/(mg·min),时间单位为 min。该工况下穿透中点约在 100 min,
穿透发生之前出水浓度远低于进料浓度。
"""

from __future__ import annotations

REFERENCE_CASE = {
    "name": "软化床参考工况(钠型树脂除硬度)",
    "c0": 100.0,     # 进料硬度浓度, mg/L
    "flow": 10.0,    # 体积流量, L/min
    "q0": 50.0,      # 床层单位吸附容量, mg/g
    "k_th": 0.005,   # Thomas 速率常数, L/(mg·min)
    "mass": 2000.0,  # 填料质量, g
}
