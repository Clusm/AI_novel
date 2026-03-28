"""
统一配置管理模块

整合所有配置项到单一入口，提供：
1. 类型安全的配置访问
2. 配置持久化
3. 热重载支持
4. 默认值管理

配置文件位置：
- Windows: %APPDATA%/AI_Novel_Writer/
- macOS/Linux: ~/.config/AI_Novel_Writer/
"""

import os
import sys
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime


def _get_config_dir() -> str:
    """获取配置文件目录"""
    if sys.platform == "win32":
        return os.path.join(os.environ["APPDATA"], "AI_Novel_Writer")
    return os.path.join(os.path.expanduser("~"), ".config", "AI_Novel_Writer")


def _get_default_workspace() -> str:
    """获取默认工作空间路径"""
    try:
        if sys.platform == "win32":
            import ctypes.wintypes
            CSIDL_PERSONAL = 5
            SHGFP_TYPE_CURRENT = 0
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
            docs_dir = buf.value
        else:
            docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
    except Exception:
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
    return os.path.join(docs_dir, "AI_Novel_Projects")


@dataclass
class ModelParams:
    """模型参数配置"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: Optional[int] = None


@dataclass
class AppConfig:
    """应用配置（统一入口）"""
    
    # ===== 路径配置 =====
    workspace_path: str = field(default_factory=_get_default_workspace)
    config_dir: str = field(default_factory=_get_config_dir)
    
    # ===== API 配置 =====
    deepseek_api_key: str = ""
    dashscope_api_key: str = ""
    moonshot_api_key: str = ""
    auth_code: str = ""
    
    # ===== 模型配置 =====
    route_profile: str = "speed"
    writer_model: str = "auto"
    model_preset: str = "default"
    
    # ===== 按角色模型参数 =====
    model_params_by_role: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    model_defaults_by_role: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # ===== 生成配置 =====
    chapter_min_chars: int = 3500
    chapter_max_chars: int = 5500
    chapter_min_chars_tomato: int = 2100
    chapter_max_chars_tomato: int = 2600
    chapter_summary_max_chars: int = 900
    kickoff_timeout: int = 1500
    story_bible_refresh_every: int = 5
    
    # ===== 功能开关 =====
    enable_memory: bool = False
    enable_dedup: bool = True
    chapter_opening_similarity_threshold: float = 0.74
    
    # ===== 元数据 =====
    last_modified: Optional[str] = None
    
    # ===== 配置文件路径 =====
    _config_file: str = field(default="", repr=False)
    _api_keys_file: str = field(default="", repr=False)
    _encryption_key_file: str = field(default="", repr=False)
    
    def __post_init__(self):
        self.config_dir = _get_config_dir()
        self._config_file = os.path.join(self.config_dir, "config.json")
        self._api_keys_file = os.path.join(self.config_dir, ".api_keys.enc")
        self._encryption_key_file = os.path.join(self.config_dir, ".encryption_key")
        
        if not self.model_params_by_role:
            self.model_params_by_role = {role: {} for role in self.get_model_roles()}
        if not self.model_defaults_by_role:
            self.model_defaults_by_role = {role: {} for role in self.get_model_roles()}
    
    @staticmethod
    def get_model_roles() -> tuple:
        """获取模型角色列表"""
        return ("outline", "character", "writer", "finalizer")
    
    @staticmethod
    def get_model_role_labels() -> Dict[str, str]:
        """获取模型角色标签映射"""
        return {
            "outline": "大纲优化师",
            "character": "人物守护者",
            "writer": "主写手",
            "finalizer": "终极审校",
        }
    
    @staticmethod
    def get_route_profiles() -> Dict[str, str]:
        """获取路由策略选项"""
        return {
            "speed": "极速 (Speed)",
            "balanced": "平衡 (Balanced)",
            "quality": "质量 (Quality)",
        }
    
    @staticmethod
    def get_writer_models() -> List[str]:
        """获取主写模型选项"""
        return ["auto", "qwen", "kimi"]
    
    @classmethod
    def load(cls) -> "AppConfig":
        """从文件加载配置"""
        config = cls()
        
        os.makedirs(config.config_dir, exist_ok=True)
        
        config._load_workspace_config()
        config._load_api_keys()
        
        return config
    
    def _load_workspace_config(self):
        """加载工作空间配置"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.workspace_path = data.get("workspace_path", self.workspace_path)
            except Exception:
                pass
    
    def _load_api_keys(self):
        """加载 API 配置（解密）"""
        try:
            from cryptography.fernet import Fernet
            
            if not os.path.exists(self._api_keys_file):
                return
            
            key = self._get_or_create_encryption_key()
            fernet = Fernet(key)
            
            with open(self._api_keys_file, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode())
            
            self.deepseek_api_key = keys.get("DEEPSEEK_API_KEY", "")
            self.dashscope_api_key = keys.get("DASHSCOPE_API_KEY", "")
            self.moonshot_api_key = keys.get("MOONSHOT_API_KEY", "")
            self.auth_code = keys.get("AUTH_CODE", "")
            self.route_profile = keys.get("ROUTE_PROFILE", "speed")
            self.writer_model = keys.get("WRITER_MODEL", "auto")
            self.model_preset = keys.get("MODEL_PRESET", "default")
            self.model_params_by_role = keys.get("MODEL_PARAMS_BY_ROLE", {})
            self.model_defaults_by_role = keys.get("MODEL_DEFAULTS_BY_ROLE", {})
            
        except Exception:
            pass
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        if os.path.exists(self._encryption_key_file):
            with open(self._encryption_key_file, "rb") as f:
                return f.read()
        
        from cryptography.fernet import Fernet
        key = Fernet.generate_key()
        with open(self._encryption_key_file, "wb") as f:
            f.write(key)
        return key
    
    def save(self):
        """保存配置到文件"""
        os.makedirs(self.config_dir, exist_ok=True)
        
        self._save_workspace_config()
        self._save_api_keys()
        
        self.last_modified = datetime.now().isoformat()
    
    def _save_workspace_config(self):
        """保存工作空间配置"""
        data = {"workspace_path": self.workspace_path}
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_api_keys(self):
        """保存 API 配置（加密）"""
        from cryptography.fernet import Fernet
        
        keys = {
            "DEEPSEEK_API_KEY": self.deepseek_api_key,
            "DASHSCOPE_API_KEY": self.dashscope_api_key,
            "MOONSHOT_API_KEY": self.moonshot_api_key,
            "AUTH_CODE": self.auth_code,
            "ROUTE_PROFILE": self.route_profile,
            "WRITER_MODEL": self.writer_model,
            "CREWAI_ENABLE_MEMORY": False,
            "MODEL_PRESET": self.model_preset,
            "MODEL_PARAMS_BY_ROLE": self.model_params_by_role,
            "MODEL_DEFAULTS_BY_ROLE": self.model_defaults_by_role,
            "MODEL_PARAMS": dict(self.model_params_by_role.get("writer", {})),
        }
        
        key = self._get_or_create_encryption_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(json.dumps(keys).encode())
        
        with open(self._api_keys_file, "wb") as f:
            f.write(encrypted_data)
    
    def get_projects_dir(self) -> str:
        """获取项目目录路径"""
        return os.path.join(self.workspace_path, "projects")
    
    def get_chapter_min_chars(self, style: str = "standard") -> int:
        """获取章节最小字数"""
        if style == "tomato":
            return self.chapter_min_chars_tomato
        return self.chapter_min_chars
    
    def get_chapter_max_chars(self, style: str = "standard") -> int:
        """获取章节最大字数"""
        if style == "tomato":
            return self.chapter_max_chars_tomato
        return self.chapter_max_chars
    
    def has_api_key(self, provider: str) -> bool:
        """检查是否配置了指定提供商的 API Key"""
        key_map = {
            "deepseek": self.deepseek_api_key,
            "qwen": self.dashscope_api_key,
            "dashscope": self.dashscope_api_key,
            "kimi": self.moonshot_api_key,
            "moonshot": self.moonshot_api_key,
        }
        return bool((key_map.get(provider, "") or "").strip())
    
    def get_model_params(self, role: str) -> Dict[str, Any]:
        """获取指定角色的模型参数"""
        if self.model_preset == "custom" and role in self.model_params_by_role:
            return self.model_params_by_role[role]
        return self.model_defaults_by_role.get(role, {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": None,
        })
    
    def set_model_params(self, role: str, params: Dict[str, Any]):
        """设置指定角色的模型参数"""
        self.model_params_by_role[role] = params
    
    def to_api_keys_dict(self) -> Dict[str, Any]:
        """转换为 API keys 字典格式（兼容旧代码）"""
        return {
            "DEEPSEEK_API_KEY": self.deepseek_api_key,
            "DASHSCOPE_API_KEY": self.dashscope_api_key,
            "MOONSHOT_API_KEY": self.moonshot_api_key,
            "AUTH_CODE": self.auth_code,
            "ROUTE_PROFILE": self.route_profile,
            "WRITER_MODEL": self.writer_model,
            "CREWAI_ENABLE_MEMORY": False,
            "MODEL_PRESET": self.model_preset,
            "MODEL_PARAMS_BY_ROLE": self.model_params_by_role,
            "MODEL_DEFAULTS_BY_ROLE": self.model_defaults_by_role,
            "MODEL_PARAMS": dict(self.model_params_by_role.get("writer", {})),
        }
    
    @classmethod
    def from_api_keys_dict(cls, keys: Dict[str, Any]) -> "AppConfig":
        """从 API keys 字典创建配置（兼容旧代码）"""
        config = cls()
        config.deepseek_api_key = keys.get("DEEPSEEK_API_KEY", "")
        config.dashscope_api_key = keys.get("DASHSCOPE_API_KEY", "")
        config.moonshot_api_key = keys.get("MOONSHOT_API_KEY", "")
        config.auth_code = keys.get("AUTH_CODE", "")
        config.route_profile = keys.get("ROUTE_PROFILE", "speed")
        config.writer_model = keys.get("WRITER_MODEL", "auto")
        config.model_preset = keys.get("MODEL_PRESET", "default")
        config.model_params_by_role = keys.get("MODEL_PARAMS_BY_ROLE", {})
        config.model_defaults_by_role = keys.get("MODEL_DEFAULTS_BY_ROLE", {})
        return config


_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """获取全局配置实例（单例）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig.load()
    return _config_instance


def reload_config() -> AppConfig:
    """重新加载配置"""
    global _config_instance
    _config_instance = AppConfig.load()
    return _config_instance
