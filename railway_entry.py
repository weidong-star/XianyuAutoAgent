"""Railway 入口 — 健康检查 HTTP + XianyuAutoAgent（纯 Python，零 shell 依赖）"""
import os, sys, asyncio, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", "8080"))
    srv = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"[Railway] Health check listening on 0.0.0.0:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    # 1. 启动健康检查 HTTP（Railway 需要端口监听）
    threading.Thread(target=start_health_server, daemon=True).start()

    # 2. 加载配置（跳过交互式输入 — 所有变量通过 Railway Variables 提供）
    from dotenv import load_dotenv
    from loguru import logger

    if os.path.exists(".env"):
        load_dotenv()
    if os.path.exists(".env.example"):
        load_dotenv(".env.example")

    logger.remove()
    logger.add(
        sys.stderr,
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"
    )

    # 3. 校验必要配置
    cookies_str = os.getenv("COOKIES_STR")
    if not cookies_str or cookies_str == "your_cookies_here":
        logger.error("COOKIES_STR 未设置！请在 Railway Variables 中添加。")
        sys.exit(1)

    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.warning("API_KEY 未设置，AI 回复将不可用")

    # 4. 启动 XianyuLive（复制 main.py 的启动逻辑，但跳过交互式 check）
    from XianyuApis import XianyuApis
    from XianyuAgent import XianyuReplyBot
    from context_manager import ChatContextManager
    from utils.xianyu_utils import generate_device_id, trans_cookies

    # 预热 ReplyBot（加载 prompt 模板等）
    XianyuReplyBot()

    # 导入并实例化 XianyuLive
    # 由于 main.py 中的 XianyuLive 类定义在 __main__ 块之前，
    # 我们用 importlib 加载而不触发 main 的 if __name__ == "__main__"
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "main_mod", os.path.join(os.path.dirname(__file__), "main.py")
    )
    main_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_mod)

    # 直接调用 main_mod 中的 XianyuLive
    xianyu_live = main_mod.XianyuLive(cookies_str)
    logger.info("XianyuAutoAgent 启动中...")
    asyncio.run(xianyu_live.main())
