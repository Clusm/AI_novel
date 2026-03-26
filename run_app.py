import os
import sys
import time
import traceback

def log_error(msg):
    try:
        if sys.platform == "win32":
            log_dir = os.path.join(os.environ.get("APPDATA", "."), "AI_Novel_Writer", "logs")
        else:
            log_dir = os.path.join(os.path.expanduser("~"), ".config", "AI_Novel_Writer", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "ai_novel_startup.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except:
        pass

def global_exception_handler(exc_type, exc_value, exc_traceback):
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_error(f"FATAL ERROR:\n{error_msg}")
    print(f"FATAL ERROR:\n{error_msg}")
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = global_exception_handler

log_error("程序启动开始...")

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

log_error("设置环境变量...")

if sys.platform == "win32":
    _crewai_base = os.path.join(os.environ["APPDATA"], "AI_Novel_Writer", "crewai")
else:
    _crewai_base = os.path.join(os.path.expanduser("~"), ".config", "AI_Novel_Writer", "crewai")

os.makedirs(_crewai_base, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = os.path.join(_crewai_base, "data")
os.environ["CREWAI_CACHE_DIR"] = os.path.join(_crewai_base, "cache")

log_error("导入 main_gui 模块...")

try:
    from main_gui import main
    log_error("main_gui 导入成功")
except Exception as e:
    log_error(f"导入 main_gui 失败: {e}")
    raise


if __name__ == "__main__":
    # 如果是打包后的冻结环境（即 exe 运行）
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        os.chdir(exe_dir)
        
        # 确定日志路径在 AppData 目录下，避免 C 盘权限问题导致无法写入日志
        if sys.platform == "win32":
            log_dir = os.path.join(os.environ.get("APPDATA", exe_dir), "AI_Novel_Writer", "logs")
        else:
            log_dir = os.path.join(os.path.expanduser("~"), ".config", "AI_Novel_Writer", "logs")
            
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "ai_novel_startup.log")
            log_fp = open(log_path, "a", encoding="utf-8", buffering=1)
            sys.stdout = log_fp
            sys.stderr = log_fp
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] EXE 启动，工作目录: {exe_dir}")
        except Exception:
            pass
    # 启动主 GUI
    sys.exit(main())
