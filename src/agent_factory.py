"""
Agent 工厂模块

提供配置驱动的 Agent 创建：
1. 从 YAML 配置加载 Agent 定义
2. 支持模型路由策略
3. 支持自定义 Agent 注册
"""

import os
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass
from abc import ABC, abstractmethod

import yaml


@dataclass
class AgentConfig:
    """Agent 配置数据类"""
    role: str
    goal: str
    backstory: str
    model_provider: str = "qwen"
    max_iter: int = 3
    max_execution_time: int = 600
    verbose: bool = True
    allow_delegation: bool = False
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: Optional[int] = None


class AgentFactory:
    """
    Agent 工厂
    
    从配置文件创建 Agent 实例，支持：
    1. YAML 配置驱动
    2. 模型路由策略
    3. 参数预设
    
    使用示例:
        factory = AgentFactory()
        
        # 加载配置
        factory.load_config()
        
        # 创建所有 Agent
        agents = factory.create_agents(route_profile="speed")
        
        # 创建单个 Agent
        writer = factory.create_agent("writer")
    """
    
    _config: Dict[str, Any] = {}
    _config_loaded: bool = False
    
    @classmethod
    def get_config_path(cls) -> str:
        """获取配置文件路径"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "config", "agents.yaml")
    
    @classmethod
    def load_config(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置文件
        
        参数:
            config_path: 配置文件路径（可选）
        
        返回:
            配置字典
        """
        if cls._config_loaded and not config_path:
            return cls._config
        
        path = config_path or cls.get_config_path()
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Agent 配置文件不存在: {path}")
        
        with open(path, "r", encoding="utf-8") as f:
            cls._config = yaml.safe_load(f)
        
        cls._config_loaded = True
        return cls._config
    
    @classmethod
    def get_agent_config(cls, role: str) -> AgentConfig:
        """
        获取指定角色的配置
        
        参数:
            role: 角色名称（outline/character/writer/finalizer）
        
        返回:
            AgentConfig 实例
        """
        config = cls.load_config()
        agents_config = config.get("agents", {})
        
        if role not in agents_config:
            raise ValueError(f"未找到 Agent 配置: {role}")
        
        agent_data = agents_config[role]
        
        return AgentConfig(
            role=agent_data.get("role", role),
            goal=agent_data.get("goal", ""),
            backstory=agent_data.get("backstory", ""),
            model_provider=agent_data.get("model_provider", "qwen"),
            max_iter=agent_data.get("max_iter", 3),
            max_execution_time=agent_data.get("max_execution_time", 600),
            verbose=agent_data.get("verbose", True),
            allow_delegation=agent_data.get("allow_delegation", False),
            temperature=agent_data.get("temperature", 0.7),
            top_p=agent_data.get("top_p", 0.9),
            max_tokens=agent_data.get("max_tokens"),
        )
    
    @classmethod
    def get_model_for_role(cls, role: str, route_profile: str = "speed") -> str:
        """
        根据路由策略获取模型
        
        参数:
            role: 角色名称
            route_profile: 路由策略（speed/balanced/quality）
        
        返回:
            模型提供商名称
        """
        config = cls.load_config()
        routing = config.get("model_routing", {})
        
        profile_routing = routing.get(route_profile, routing.get("speed", {}))
        
        return profile_routing.get(role, "qwen")
    
    @classmethod
    def create_agent(
        cls,
        role: str,
        route_profile: str = "speed",
        llm_override: Optional[Any] = None,
        **kwargs,
    ):
        """
        创建单个 Agent
        
        参数:
            role: 角色名称
            route_profile: 路由策略
            llm_override: 自定义 LLM 实例
            **kwargs: 额外参数覆盖
        
        返回:
            Agent 实例
        """
        from crewai import Agent, LLM
        
        agent_config = cls.get_agent_config(role)
        
        model_provider = cls.get_model_for_role(role, route_profile)
        
        if llm_override:
            llm = llm_override
        else:
            llm = cls._create_llm(model_provider, agent_config)
        
        agent_kwargs = {
            "role": kwargs.get("role", agent_config.role),
            "goal": kwargs.get("goal", agent_config.goal),
            "backstory": kwargs.get("backstory", agent_config.backstory),
            "llm": llm,
            "max_iter": kwargs.get("max_iter", agent_config.max_iter),
            "max_execution_time": kwargs.get("max_execution_time", agent_config.max_execution_time),
            "verbose": kwargs.get("verbose", agent_config.verbose),
            "allow_delegation": kwargs.get("allow_delegation", agent_config.allow_delegation),
        }
        
        return Agent(**agent_kwargs)
    
    @classmethod
    def create_agents(
        cls,
        route_profile: str = "speed",
        roles: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        创建多个 Agent
        
        参数:
            route_profile: 路由策略
            roles: 要创建的角色列表（可选，默认全部）
            **kwargs: 传递给每个 Agent 的额外参数
        
        返回:
            角色到 Agent 实例的映射
        """
        config = cls.load_config()
        agents_config = config.get("agents", {})
        
        if roles is None:
            roles = list(agents_config.keys())
        
        agents = {}
        for role in roles:
            agents[role] = cls.create_agent(role, route_profile, **kwargs.get(role, {}))
        
        return agents
    
    @classmethod
    def _create_llm(cls, provider: str, config: AgentConfig) -> Any:
        """
        创建 LLM 实例
        
        参数:
            provider: 模型提供商
            config: Agent 配置
        
        返回:
            LLM 实例
        """
        from crewai import LLM
        from src.api import load_api_keys
        
        keys = load_api_keys()
        
        model_map = {
            "deepseek": {
                "model": "deepseek/deepseek-chat",
                "api_key": keys.get("DEEPSEEK_API_KEY", ""),
                "base_url": "https://api.deepseek.com",
            },
            "qwen": {
                "model": "openai/qwen-max",
                "api_key": keys.get("DASHSCOPE_API_KEY", ""),
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            },
            "kimi": {
                "model": "openai/kimi-k2.5",
                "api_key": keys.get("MOONSHOT_API_KEY", ""),
                "base_url": "https://api.moonshot.cn/v1",
            },
        }
        
        llm_config = model_map.get(provider, model_map["qwen"])
        model_name = llm_config["model"]
        
        model_lower = model_name.lower()
        is_reasoner = any(p in model_lower for p in ["deepseek-reasoner", "openai/o1", "openai/o3", "kimi-k2"])
        
        if is_reasoner:
            llm_kwargs = {
                "model": model_name,
                "api_key": llm_config["api_key"],
                "base_url": llm_config["base_url"],
            }
            if config.max_tokens is not None:
                llm_kwargs["max_tokens"] = config.max_tokens
        else:
            llm_kwargs = {
                "model": model_name,
                "api_key": llm_config["api_key"],
                "base_url": llm_config["base_url"],
                "temperature": config.temperature,
                "top_p": config.top_p,
                "max_tokens": config.max_tokens,
            }
        
        return LLM(**llm_kwargs)
    
    @classmethod
    def get_prompt_template(cls, template_name: str) -> str:
        """
        获取提示词模板
        
        参数:
            template_name: 模板名称
        
        返回:
            模板内容
        """
        config = cls.load_config()
        templates = config.get("prompt_templates", {})
        return templates.get(template_name, "")
    
    @classmethod
    def get_model_preset(cls, preset_name: str) -> Dict[str, Any]:
        """
        获取模型参数预设
        
        参数:
            preset_name: 预设名称
        
        返回:
            参数字典
        """
        config = cls.load_config()
        presets = config.get("model_presets", {})
        return presets.get(preset_name, presets.get("default", {}))
    
    @classmethod
    def list_roles(cls) -> List[str]:
        """
        列出所有可用的角色
        
        返回:
            角色名称列表
        """
        config = cls.load_config()
        return list(config.get("agents", {}).keys())
    
    @classmethod
    def reload_config(cls) -> None:
        """重新加载配置"""
        cls._config_loaded = False
        cls._config = {}
        cls.load_config()
