import os
import json
import sys
import ctypes
from pathlib import Path

# User config file location
if sys.platform == "win32":
    CONFIG_DIR = os.path.join(os.environ["APPDATA"], "AI_Novel_Writer")
else:
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "ai_novel_writer")

CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class WorkspaceManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkspaceManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def _init(self):
        self.workspace_path = None
        self.load_config()
        
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.workspace_path = data.get("workspace_path")
            except Exception:
                pass
                
    def save_config(self):
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        data = {
            "workspace_path": self.workspace_path
        }
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    def get_workspace(self):
        return self.workspace_path
        
    def set_workspace(self, path):
        self.workspace_path = path
        self.save_config()
        
    def get_projects_dir(self):
        if not self.workspace_path:
            # Fallback to user documents directory to avoid permission issues in Program Files
            try:
                if sys.platform == "win32":
                    import ctypes.wintypes
                    CSIDL_PERSONAL = 5       # My Documents
                    SHGFP_TYPE_CURRENT = 0   # Get current, not default value
                    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
                    docs_dir = buf.value
                else:
                    docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
            except Exception:
                docs_dir = os.path.join(os.path.expanduser("~"), "Documents")

            default_workspace = os.path.join(docs_dir, "AI_Novel_Projects")
            
            # If we are falling back, let's try to set it as the default workspace
            # so the user knows where their files are going.
            self.workspace_path = default_workspace
            self.save_config()
            
            return os.path.join(self.workspace_path, "projects")
            
        return os.path.join(self.workspace_path, "projects")

# Global instance
workspace_manager = WorkspaceManager()
