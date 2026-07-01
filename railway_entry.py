"""Railway 入口 - 诊断版（查看实际环境变量）"""
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
    threading.Thread(target=start_health_server, daemon=True).start()

    # DIAGNOSTIC: 打印所有包含 cookie/key 的环境变量
    print("[DIAG] Checking environment variables...")
    for k, v in sorted(os.environ.items()):
        low = k.lower()
        if any(w in low for w in ["cookie", "api", "model", "key"]):
            masked = v[:10] + "..." if len(v) > 10 else v
            print(f"  ENV: {k} = {masked}")

    cookies_str = os.environ.get("COOKIES_STR") or os.getenv("COOKIES_STR")
    if not cookies_str:
        print("[DIAG] COOKIES_STR not found!")
        print("[DIAG] First 30 env keys:", list(os.environ.keys())[:30])
        sys.exit(1)

    print(f"[DIAG] COOKIES_STR found, length={len(cookies_str)}")

    from dotenv import load_dotenv
    from loguru import logger

    if os.path.exists(".env"):
        load_dotenv()
    if os.path.exists(".env.example"):
        load_dotenv(".env.example")

    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <level>{message}</level>"
    )

    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.warning("API_KEY 未设置，AI 回复将不可用")

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "main_mod", os.path.join(os.path.dirname(__file__), "main.py")
    )
    main_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_mod)

    xianyu_live = main_mod.XianyuLive(cookies_str)
    logger.info("XianyuAutoAgent 启动中...")
    asyncio.run(xianyu_live.main())
