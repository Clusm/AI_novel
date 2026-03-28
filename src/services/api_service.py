"""
API 服务模块

封装 API 相关的业务逻辑：
1. API Key 管理
2. 连接测试
3. 模型配置
"""

from typing import Dict, Tuple, List, Optional, Any

from src.api import (
    load_api_keys,
    save_api_keys,
    test_api_connection,
    test_all_apis,
)
from src.exceptions import (
    APIKeyMissingError,
    APIConnectionError,
)


class APIService:
    """
    API 服务
    
    封装 API 配置和测试的所有操作。
    
    使用示例:
        service = APIService()
        
        # 加载 API Keys
        keys = service.load_keys()
        
        # 保存 API Keys
        service.save_keys({"DEEPSEEK_API_KEY": "sk-xxx"})
        
        # 测试连接
        success, message = service.test_connection("deepseek")
    """
    
    PROVIDERS = {
        "deepseek": {
            "name": "DeepSeek",
            "key_prefix": "DEEPSEEK_API_KEY",
            "models": ["deepseek-chat", "deepseek-reasoner"],
        },
        "qwen": {
            "name": "通义千问",
            "key_prefix": "DASHSCOPE_API_KEY",
            "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
        },
        "kimi": {
            "name": "Kimi (Moonshot)",
            "key_prefix": "MOONSHOT_API_KEY",
            "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        },
    }
    
    def __init__(self):
        pass
    
    def load_keys(self) -> Dict[str, Any]:
        """
        加载 API Keys
        
        返回:
            API Keys 字典
        """
        return load_api_keys()
    
    def save_keys(self, keys: Dict[str, Any]) -> None:
        """
        保存 API Keys
        
        参数:
            keys: API Keys 字典
        """
        save_api_keys(keys)
    
    def get_key(self, provider: str) -> str:
        """
        获取指定提供商的 API Key
        
        参数:
            provider: 提供商名称（deepseek/qwen/kimi）
        
        返回:
            API Key（可能为空字符串）
        """
        keys = self.load_keys()
        provider_info = self.PROVIDERS.get(provider, {})
        key_name = provider_info.get("key_prefix", f"{provider.upper()}_API_KEY")
        return keys.get(key_name, "")
    
    def set_key(self, provider: str, api_key: str) -> None:
        """
        设置指定提供商的 API Key
        
        参数:
            provider: 提供商名称
            api_key: API Key
        """
        keys = self.load_keys()
        provider_info = self.PROVIDERS.get(provider, {})
        key_name = provider_info.get("key_prefix", f"{provider.upper()}_API_KEY")
        keys[key_name] = api_key
        self.save_keys(keys)
    
    def has_key(self, provider: str) -> bool:
        """
        检查是否配置了 API Key
        
        参数:
            provider: 提供商名称
        
        返回:
            是否已配置
        """
        key = self.get_key(provider)
        return bool(key and key.strip())
    
    def test_connection(self, provider: str) -> Tuple[bool, str]:
        """
        测试 API 连接
        
        参数:
            provider: 提供商名称
        
        返回:
            (是否成功, 消息)
        """
        if not self.has_key(provider):
            return False, f"未配置 {self.PROVIDERS.get(provider, {}).get('name', provider)} API Key"
        
        return test_api_connection(provider)
    
    def test_all(self) -> Dict[str, Tuple[bool, str]]:
        """
        测试所有 API 连接
        
        返回:
            提供商到测试结果的映射
        """
        return test_all_apis()
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """
        获取提供商信息
        
        参数:
            provider: 提供商名称
        
        返回:
            提供商信息字典
        """
        return self.PROVIDERS.get(provider, {})
    
    def get_all_providers(self) -> List[str]:
        """
        获取所有支持的提供商
        
        返回:
            提供商名称列表
        """
        return list(self.PROVIDERS.keys())
    
    def get_provider_name(self, provider: str) -> str:
        """
        获取提供商显示名称
        
        参数:
            provider: 提供商标识
        
        返回:
            显示名称
        """
        return self.PROVIDERS.get(provider, {}).get("name", provider)
    
    def get_route_profile(self) -> str:
        """
        获取当前路由策略
        
        返回:
            路由策略（speed/balanced/quality）
        """
        keys = self.load_keys()
        return keys.get("ROUTE_PROFILE", "speed")
    
    def set_route_profile(self, profile: str) -> None:
        """
        设置路由策略
        
        参数:
            profile: 路由策略
        """
        if profile not in ("speed", "balanced", "quality"):
            profile = "speed"
        
        keys = self.load_keys()
        keys["ROUTE_PROFILE"] = profile
        self.save_keys(keys)
    
    def get_writer_model(self) -> str:
        """
        获取主写模型设置
        
        返回:
            主写模型（auto/qwen/kimi）
        """
        keys = self.load_keys()
        return keys.get("WRITER_MODEL", "auto")
    
    def set_writer_model(self, model: str) -> None:
        """
        设置主写模型
        
        参数:
            model: 主写模型
        """
        if model not in ("auto", "qwen", "kimi"):
            model = "auto"
        
        keys = self.load_keys()
        keys["WRITER_MODEL"] = model
        self.save_keys(keys)
    
    def get_model_preset(self) -> str:
        """
        获取模型参数预设
        
        返回:
            预设名称（default/custom）
        """
        keys = self.load_keys()
        return keys.get("MODEL_PRESET", "default")
    
    def set_model_preset(self, preset: str) -> None:
        """
        设置模型参数预设
        
        参数:
            preset: 预设名称
        """
        keys = self.load_keys()
        keys["MODEL_PRESET"] = preset
        self.save_keys(keys)
    
    def get_model_params(self, role: str) -> Dict[str, Any]:
        """
        获取指定角色的模型参数
        
        参数:
            role: 角色名称（outline/character/writer/finalizer）
        
        返回:
            模型参数字典
        """
        keys = self.load_keys()
        params_by_role = keys.get("MODEL_PARAMS_BY_ROLE", {})
        return params_by_role.get(role, {})
    
    def set_model_params(self, role: str, params: Dict[str, Any]) -> None:
        """
        设置指定角色的模型参数
        
        参数:
            role: 角色名称
            params: 模型参数
        """
        keys = self.load_keys()
        params_by_role = keys.get("MODEL_PARAMS_BY_ROLE", {})
        params_by_role[role] = params
        keys["MODEL_PARAMS_BY_ROLE"] = params_by_role
        self.save_keys(keys)
    
    def validate_key_format(self, provider: str, api_key: str) -> Tuple[bool, str]:
        """
        验证 API Key 格式
        
        参数:
            provider: 提供商名称
            api_key: API Key
        
        返回:
            (是否有效, 消息)
        """
        if not api_key or not api_key.strip():
            return False, "API Key 不能为空"
        
        api_key = api_key.strip()
        
        if provider == "deepseek":
            if not api_key.startswith("sk-"):
                return False, "DeepSeek API Key 应以 'sk-' 开头"
        elif provider == "qwen":
            if len(api_key) < 20:
                return False, "通义千问 API Key 格式不正确"
        elif provider == "kimi":
            if not api_key.startswith("sk-"):
                return False, "Kimi API Key 应以 'sk-' 开头"
        
        return True, "格式正确"
