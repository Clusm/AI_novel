import os
import sys
from PySide6.QtWidgets import QApplication

os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"

# Set CrewAI paths to user config directory to avoid permission issues in Program Files
if sys.platform == "win32":
    _base_dir = os.path.join(os.environ["APPDATA"], "AI_Novel_Writer", "crewai")
else:
    _base_dir = os.path.join(os.path.expanduser("~"), ".config", "ai_novel_writer", "crewai")

os.makedirs(_base_dir, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = os.path.join(_base_dir, "data")
os.environ["CREWAI_CACHE_DIR"] = os.path.join(_base_dir, "cache")

from gui.main_window import MainWindow
from gui.workspace_dialog import WorkspaceDialog
from src.workspace import workspace_manager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("多Agent写作系统 Pro")
    
    # Check for workspace
    if not workspace_manager.get_workspace():
        dialog = WorkspaceDialog()
        if dialog.exec() == WorkspaceDialog.Accepted:
            workspace_manager.set_workspace(dialog.selected_path)
        else:
            return 0
            
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
