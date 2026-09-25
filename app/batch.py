"""批量工况调度:逐条独立求解,各工况之间互不累加、互不覆盖。

每条工况都调用一次 :func:`service.run_case`,其内部全部使用新建的
局部数据结构,模块层面不保存任何可变的中间状态,因此批量结果与逐条
单独计算完全一致,且与工况的提交顺序无关。
"""

from __future__ import annotations

from . import service, validation


def run_batch(
    cases: object,
    points: object = None,
    threshold: object = None,
) -> list[dict]:
    """按顺序逐条求解工况列表,每条产出一个独立结果条目。

    单条工况校验失败只影响该条目(``ok=False`` 并附原因),不影响
    其余工况的计算。
    """
    if not isinstance(cases, list):
        raise validation.ValidationError(f"cases 必须是数组,收到: {cases!r}")
    results = []
    for index, payload in enumerate(cases):
        entry: dict = {"index": index}
        if isinstance(payload, dict) and "name" in payload:
            entry["name"] = payload["name"]
        try:
            entry["result"] = service.run_case(
                payload, points=points, threshold=threshold
            )
        except validation.ValidationError as exc:
            entry["ok"] = False
            entry["error"] = str(exc)
        else:
            entry["ok"] = True
        results.append(entry)
    return results
