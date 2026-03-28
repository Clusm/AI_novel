"""
控制器基类模块 (PySide6 版本)

提供控制器的通用功能：
1. 服务管理
2. 信号定义
3. 错误处理
"""

from typing import Any, Dict, Optional, Callable
from PySide6.QtCore import QObject, Signal


class BaseController(QObject):
    """
    控制器基类
    
    所有控制器的基类，提供通用功能。
    """
    
    error_occurred = Signal(str)
    info_message = Signal(str)
    success_message = Signal(str)
    warning_message = Signal(str)
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._services: Dict[str, Any] = {}
        self._log_callback: Optional[Callable[[str, str], None]] = None
    
    def register_service(self, name: str, service: Any) -> None:
        """注册服务实例"""
        self._services[name] = service
    
    def get_service(self, name: str) -> Optional[Any]:
        """获取服务实例"""
        if name not in self._services:
            from src.container import Container
            return Container.get(name)
        return self._services.get(name)
    
    def set_log_callback(self, callback: Callable[[str, str], None]) -> None:
        """设置日志回调函数"""
        self._log_callback = callback
    
    def _log(self, message: str, status: str = "info") -> None:
        """记录日志"""
        if self._log_callback:
            self._log_callback(message, status)
        
        from src.logger import log_manager
        from src.logger import LogLevel
        
        level_map = {
            "info": LogLevel.INFO,
            "success": LogLevel.SUCCESS,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
        }
        log_manager._log(
            level_map.get(status, LogLevel.INFO),
            message,
            module=self.__class__.__name__
        )
    
    def info(self, message: str) -> None:
        """记录信息日志"""
        self._log(message, "info")
        self.info_message.emit(message)
    
    def success(self, message: str) -> None:
        """记录成功日志"""
        self._log(message, "success")
        self.success_message.emit(message)
    
    def warning(self, message: str) -> None:
        """记录警告日志"""
        self._log(message, "warning")
        self.warning_message.emit(message)
    
    def error(self, message: str) -> None:
        """记录错误日志"""
        self._log(message, "error")
        self.error_occurred.emit(message)
    
    def handle_exception(self, e: Exception, context: str = "") -> None:
        """处理异常"""
        from src.exceptions import NovelWriterError
        
        if isinstance(e, NovelWriterError):
            message = str(e)
        else:
            message = f"{context}: {str(e)}" if context else str(e)
        
        self.error(message)
