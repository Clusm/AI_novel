"""
统一日志管理模块

提供：
1. 多处理器支持（文件、UI、控制台）
2. 结构化日志格式
3. 日志级别管理
4. 向后兼容旧代码
"""

import os
import sys
import logging
from datetime import datetime
from typing import Callable, List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: datetime
    level: LogLevel
    module: str
    message: str
    status: str = "info"
    details: Optional[Dict[str, Any]] = None
    
    def to_simple_string(self) -> str:
        """转换为简单字符串格式"""
        icon = self._get_icon()
        time_str = self.timestamp.strftime("%H:%M:%S")
        return f"{icon} **[{time_str}] {self.module}**：{self.message}"
    
    def to_html(self) -> str:
        """转换为 HTML 格式"""
        icon = self._get_icon()
        time_str = self.timestamp.strftime("%H:%M:%S")
        
        bg_colors = {
            LogLevel.ERROR: "#ffebee",
            LogLevel.SUCCESS: "#e8f5e8",
            LogLevel.WARNING: "#fff3e0",
            LogLevel.INFO: "#f5f5f5",
            LogLevel.DEBUG: "#f5f5f5",
        }
        
        bg_color = bg_colors.get(self.level, "#f5f5f5")
        return f"<div style='padding: 8px; margin: 4px 0; background-color: {bg_color}; border-radius: 4px;'>{icon} **[{time_str}] {self.module}**：{self.message}</div>"
    
    def _get_icon(self) -> str:
        """获取日志图标"""
        icons = {
            LogLevel.SUCCESS: "✅",
            LogLevel.WARNING: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.INFO: "🔄",
            LogLevel.DEBUG: "🔍",
        }
        return icons.get(self.level, "🔄")


class LogManager:
    """
    统一日志管理器
    
    支持多处理器，可同时输出到文件、UI、控制台等。
    
    使用示例:
        log = LogManager()
        
        # 注册处理器
        log.register_handler(my_ui_callback)
        
        # 记录日志
        log.info("开始生成章节", module="Generator")
        log.error("生成失败", module="Generator")
    """
    
    _instance: Optional["LogManager"] = None
    _lock = Lock()
    
    def __new__(cls) -> "LogManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._handlers: List[Callable[[LogEntry], None]] = []
        self._file_logger: Optional[logging.Logger] = None
        self._log_dir: Optional[str] = None
        self._min_level: LogLevel = LogLevel.DEBUG
        self._entries: List[LogEntry] = []
        
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        """设置文件日志器"""
        try:
            self._log_dir = self._get_log_dir()
            os.makedirs(self._log_dir, exist_ok=True)
            
            log_file = os.path.join(self._log_dir, "ai_novel_writer.log")
            
            self._file_logger = logging.getLogger("AI_Novel_Writer")
            self._file_logger.setLevel(logging.DEBUG)
            
            if not self._file_logger.handlers:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                
                formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                file_handler.setFormatter(formatter)
                self._file_logger.addHandler(file_handler)
        except Exception:
            self._file_logger = None
    
    def _get_log_dir(self) -> str:
        """获取日志目录"""
        if sys.platform == "win32":
            return os.path.join(os.environ.get("APPDATA", "."), "AI_Novel_Writer", "logs")
        return os.path.join(os.path.expanduser("~"), ".config", "AI_Novel_Writer", "logs")
    
    def register_handler(self, handler: Callable[[LogEntry], None]):
        """
        注册日志处理器
        
        处理器是一个接收 LogEntry 的回调函数，用于将日志输出到 UI 等。
        """
        self._handlers.append(handler)
    
    def unregister_handler(self, handler: Callable[[LogEntry], None]):
        """注销日志处理器"""
        if handler in self._handlers:
            self._handlers.remove(handler)
    
    def set_min_level(self, level: LogLevel):
        """设置最小日志级别"""
        self._min_level = level
    
    def _should_log(self, level: LogLevel) -> bool:
        """检查是否应该记录该级别的日志"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.SUCCESS: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
        }
        return level_order.get(level, 0) >= level_order.get(self._min_level, 0)
    
    def _log(self, level: LogLevel, message: str, module: str = "system", details: Optional[Dict] = None):
        """内部日志方法"""
        if not self._should_log(level):
            return
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            module=module,
            message=message,
            status=level.value,
            details=details,
        )
        
        self._entries.append(entry)
        
        if self._file_logger:
            log_level_map = {
                LogLevel.DEBUG: logging.DEBUG,
                LogLevel.INFO: logging.INFO,
                LogLevel.SUCCESS: logging.INFO,
                LogLevel.WARNING: logging.WARNING,
                LogLevel.ERROR: logging.ERROR,
            }
            self._file_logger.log(
                log_level_map.get(level, logging.INFO),
                f"[{module}] {message}"
            )
        
        for handler in self._handlers:
            try:
                handler(entry)
            except Exception:
                pass
    
    def debug(self, message: str, module: str = "system"):
        """记录调试日志"""
        self._log(LogLevel.DEBUG, message, module)
    
    def info(self, message: str, module: str = "system"):
        """记录信息日志"""
        self._log(LogLevel.INFO, message, module)
    
    def success(self, message: str, module: str = "system"):
        """记录成功日志"""
        self._log(LogLevel.SUCCESS, message, module)
    
    def warning(self, message: str, module: str = "system"):
        """记录警告日志"""
        self._log(LogLevel.WARNING, message, module)
    
    def error(self, message: str, module: str = "system", details: Optional[Dict] = None):
        """记录错误日志"""
        self._log(LogLevel.ERROR, message, module, details)
    
    def get_entries(self, limit: int = 100) -> List[LogEntry]:
        """获取最近的日志条目"""
        return self._entries[-limit:]
    
    def clear_entries(self):
        """清空日志条目"""
        self._entries.clear()
    
    def get_entries_html(self) -> str:
        """获取日志 HTML 格式"""
        if not self._entries:
            return "<p style='color: #666;'>暂无运行日志，开始生成后会显示在这里</p>"
        
        html = ""
        for entry in reversed(self._entries[-100:]):
            html += entry.to_html()
        return html


log_manager = LogManager()


def add_run_log(logs_list: List[str], title: str, content: str, status: str = "info") -> List[str]:
    """
    添加运行日志（向后兼容）
    
    保留此函数以兼容旧代码，同时通过 LogManager 记录。
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌" if status in ("error", "danger") else "🔄"
    log_entry = f"{icon} **[{timestamp}] {title}**：{content}"
    logs_list.append(log_entry)
    
    level_map = {
        "success": LogLevel.SUCCESS,
        "warning": LogLevel.WARNING,
        "error": LogLevel.ERROR,
        "danger": LogLevel.ERROR,
        "info": LogLevel.INFO,
    }
    log_manager._log(
        level_map.get(status, LogLevel.INFO),
        content,
        module=title
    )
    
    return logs_list


def clear_run_logs(logs_list: List[str]) -> List[str]:
    """
    清空日志（向后兼容）
    
    保留此函数以兼容旧代码。
    """
    logs_list.clear()
    return logs_list


def get_logs_html(logs_list: List[str]) -> str:
    """
    获取日志HTML格式（向后兼容）
    
    保留此函数以兼容旧代码。
    """
    if not logs_list:
        return "<p style='color: #666;'>暂无运行日志，开始生成后会显示在这里</p>"
    
    html = ""
    for log in reversed(logs_list):
        if "❌" in log:
            html += f"<div style='padding: 8px; margin: 4px 0; background-color: #ffebee; border-radius: 4px;'>{log}</div>"
        elif "✅" in log:
            html += f"<div style='padding: 8px; margin: 4px 0; background-color: #e8f5e8; border-radius: 4px;'>{log}</div>"
        else:
            html += f"<div style='padding: 8px; margin: 4px 0; background-color: #f5f5f5; border-radius: 4px;'>{log}</div>"
    return html
