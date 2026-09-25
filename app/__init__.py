"""固定床离子交换动态穿透计算服务。

按职责拆分为若干独立模块:

- ``thomas``       Thomas 解的逐点求值(穿透内核)
- ``timeaxis``     时间轴离散
- ``integrate``    浓度亏量沿时间的数值积分
- ``breakthrough`` 穿透时刻判定与爬升窗
- ``validation``   工况入参校验
- ``service``      单一工况的完整计算编排
- ``batch``        批量工况调度
- ``reference``    预置的软化床参考工况
- ``api``          Flask HTTP 接口层
"""
