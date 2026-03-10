import sys
import os
import socket
import time
import webbrowser
from threading import Thread
import streamlit.web.cli as stcli
from urllib.request import urlopen

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)


def find_available_port(start_port=8501, max_tries=30):
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port

if __name__ == "__main__":
    log_path = None
    # 当作为EXE运行时，sys.executable 指向 exe 文件路径
    # 我们希望工作目录是 exe 所在的目录，以便 user data (projects/) 存储在正确位置
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        os.chdir(exe_dir)
        # 设置 Streamlit 配置目录为 exe 所在目录
        os.environ["STREAMLIT_CONFIG_DIR"] = exe_dir
        log_path = os.path.join(exe_dir, "ai_novel_startup.log")
        try:
            log_fp = open(log_path, "a", encoding="utf-8", buffering=1)
            sys.stdout = log_fp
            sys.stderr = log_fp
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] EXE 启动，工作目录: {exe_dir}")
        except Exception:
            log_path = None

    # Streamlit 需要运行 app.py，这个文件会被打包到临时目录 (sys._MEIPASS)
    app_path = resolve_path("app.py")

    # 构造命令行参数模拟 `streamlit run app.py`
    selected_port = find_available_port()

    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--global.developmentMode=false",
        "--server.headless=true",
        f"--server.port={selected_port}",
        "--browser.serverAddress=localhost",
        "--theme.base=light",
    ]
    
    target_url = f"http://localhost:{selected_port}"

    def open_browser():
        health_url = f"{target_url}/_stcore/health"
        ready = False
        for _ in range(120):
            try:
                with urlopen(health_url, timeout=1) as resp:
                    if 200 <= resp.status < 300:
                        ready = True
                        break
            except Exception:
                pass
            time.sleep(0.5)
        try:
            if ready:
                if sys.platform.startswith("win"):
                    os.startfile(target_url)
                else:
                    webbrowser.open(target_url)
            elif log_path:
                try:
                    import tkinter as tk
                    from tkinter import messagebox

                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror("启动失败", f"服务未在预期时间内就绪，请查看日志：\n{log_path}")
                except Exception:
                    pass
        except Exception:
            pass
            
    t = Thread(target=open_browser)
    t.daemon = True
    t.start()
    
    sys.exit(stcli.main())
