"""
依赖注入容器

提供简单的依赖注入机制，用于：
1. 管理服务生命周期（单例）
2. 解耦模块依赖
3. 支持测试时替换实现

使用示例:
    # 注册服务
    Container.register("config", lambda: AppConfig.load())
    Container.register("log", lambda: LogManager())
    
    # 获取服务
    config = Container.get("config")
    log = Container.get("log")
    
    # 测试时替换
    Container.register("config", lambda: MockConfig())
"""

from typing import TypeVar, Callable, Dict, Any, Optional, List
from threading import Lock


T = TypeVar("T")


class Container:
    """
    简单的依赖注入容器
    
    特性：
    - 单例模式：每个服务只创建一次
    - 延迟加载：首次获取时才创建
    - 线程安全：使用锁保护
    - 支持重置：用于测试
    
    使用示例:
        # 注册工厂函数
        Container.register("config", lambda: AppConfig.load())
        
        # 获取实例（首次调用时创建）
        config = Container.get("config")
        
        # 检查是否已注册
        if Container.has("config"):
            ...
        
        # 重置（用于测试）
        Container.reset()
    """
    
    _instances: Dict[str, Any] = {}
    _factories: Dict[str, Callable[[], Any]] = {}
    _lock = Lock()
    
    @classmethod
    def register(cls, name: str, factory: Callable[[], T]) -> None:
        """
        注册服务工厂
        
        参数:
            name: 服务名称
            factory: 工厂函数，返回服务实例
        
        示例:
            Container.register("config", lambda: AppConfig.load())
        """
        with cls._lock:
            cls._factories[name] = factory
            if name in cls._instances:
                del cls._instances[name]
    
    @classmethod
    def get(cls, name: str) -> Optional[T]:
        """
        获取服务实例
        
        首次调用时创建实例，后续调用返回同一实例。
        
        参数:
            name: 服务名称
        
        返回:
            服务实例，如果未注册则返回 None
        
        示例:
            config = Container.get("config")
        """
        with cls._lock:
            if name in cls._instances:
                return cls._instances[name]
            
            if name not in cls._factories:
                return None
            
            instance = cls._factories[name]()
            cls._instances[name] = instance
            return instance
    
    @classmethod
    def has(cls, name: str) -> bool:
        """
        检查服务是否已注册
        
        参数:
            name: 服务名称
        
        返回:
            是否已注册
        """
        with cls._lock:
            return name in cls._factories
    
    @classmethod
    def remove(cls, name: str) -> None:
        """
        移除服务
        
        同时移除工厂和实例。
        
        参数:
            name: 服务名称
        """
        with cls._lock:
            cls._factories.pop(name, None)
            cls._instances.pop(name, None)
    
    @classmethod
    def reset(cls) -> None:
        """
        重置容器
        
        清除所有已注册的服务和实例。
        主要用于测试场景。
        """
        with cls._lock:
            cls._instances.clear()
            cls._factories.clear()
    
    @classmethod
    def reset_instances(cls) -> None:
        """
        仅重置实例
        
        保留工厂注册，清除已创建的实例。
        用于重新创建单例实例。
        """
        with cls._lock:
            cls._instances.clear()
    
    @classmethod
    def list_services(cls) -> List[str]:
        """
        列出所有已注册的服务名称
        
        返回:
            服务名称列表
        """
        with cls._lock:
            return list(cls._factories.keys())
    
    @classmethod
    def is_created(cls, name: str) -> bool:
        """
        检查服务实例是否已创建
        
        参数:
            name: 服务名称
        
        返回:
            实例是否已创建
        """
        with cls._lock:
            return name in cls._instances


def init_container():
    """
    初始化容器
    
    注册核心服务。
    应在应用启动时调用。
    """
    from src.config import AppConfig, get_config
    from src.logger import LogManager, log_manager
    from src.workspace import WorkspaceManager, workspace_manager
    
    Container.register("config", get_config)
    Container.register("log", lambda: log_manager)
    Container.register("workspace", lambda: workspace_manager)


def get_config():
    """获取配置服务（便捷方法）"""
    return Container.get("config")


def get_log():
    """获取日志服务（便捷方法）"""
    return Container.get("log")


def get_workspace():
    """获取工作空间服务（便捷方法）"""
    return Container.get("workspace")
