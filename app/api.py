"""Flask HTTP 接口层。"""

from __future__ import annotations

from flask import Flask, jsonify, request

from . import batch, reference, service, validation


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/v1/reference-case")
    def get_reference_case():
        """预置的软化床参考工况。"""
        return jsonify(reference.REFERENCE_CASE)

    @app.post("/api/v1/breakthrough")
    def single():
        """单一工况:整条曲线连同穿透时刻、累计吸附量一次算完返回。"""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "请求体必须是 JSON 对象"}), 400
        try:
            result = service.run_case(
                payload,
                points=payload.get("points"),
                threshold=payload.get("threshold"),
            )
        except validation.ValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(result)

    @app.post("/api/v1/breakthrough/batch")
    def many():
        """批量工况:一个数据集逐条推入,逐条产出各自的曲线结果。"""
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not isinstance(
            payload.get("cases"), list
        ):
            return (
                jsonify({"error": "请求体必须是包含 cases 数组的 JSON 对象"}),
                400,
            )
        try:
            results = batch.run_batch(
                payload["cases"],
                points=payload.get("points"),
                threshold=payload.get("threshold"),
            )
        except validation.ValidationError as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify({"results": results})

    return app
