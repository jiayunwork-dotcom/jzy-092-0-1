"""服务入口:``python -m app`` 在固定端口 8000 上启动 HTTP 服务。"""

from .api import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
