import os
import sys
import time

# Fix stdout/stderr for PyInstaller no-console mode
# CrewAI and Rich require valid streams for isatty checks
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# Pre-configure CrewAI paths before importing main_gui
# This ensures environment variables are set before crewai module loads
if sys.platform == "win32":
    _crewai_base = os.path.join(os.environ["APPDATA"], "AI_Novel_Writer", "crewai")
else:
    _crewai_base = os.path.join(os.path.expanduser("~"), ".config", "ai_novel_writer", "crewai")

os.makedirs(_crewai_base, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = os.path.join(_crewai_base, "data")
os.environ["CREWAI_CACHE_DIR"] = os.path.join(_crewai_base, "cache")

from main_gui import main


if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        os.chdir(exe_dir)
        
        # Determine log path in AppData to avoid permission issues
        if sys.platform == "win32":
            log_dir = os.path.join(os.environ.get("APPDATA", exe_dir), "AI_Novel_Writer", "logs")
        else:
            log_dir = os.path.join(os.path.expanduser("~"), ".config", "ai_novel_writer", "logs")
            
        try:
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, "ai_novel_startup.log")
            log_fp = open(log_path, "a", encoding="utf-8", buffering=1)
            sys.stdout = log_fp
            sys.stderr = log_fp
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] EXE 启动，工作目录: {exe_dir}")
        except Exception:
            pass
    sys.exit(main())
