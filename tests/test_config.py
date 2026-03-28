"""
配置模块测试
"""

import pytest
import os


class TestAppConfig:
    """AppConfig 测试"""
    
    def test_config_creation(self):
        """测试配置创建"""
        from src.config import AppConfig
        
        config = AppConfig()
        
        assert config.workspace_path is not None
        assert config.config_dir is not None
        assert config.route_profile == "speed"
        assert config.writer_model == "auto"
    
    def test_config_model_roles(self):
        """测试模型角色"""
        from src.config import AppConfig
        
        roles = AppConfig.get_model_roles()
        
        assert "outline" in roles
        assert "character" in roles
        assert "writer" in roles
        assert "finalizer" in roles
    
    def test_config_route_profiles(self):
        """测试路由策略"""
        from src.config import AppConfig
        
        profiles = AppConfig.get_route_profiles()
        
        assert "speed" in profiles
        assert "balanced" in profiles
        assert "quality" in profiles
    
    def test_config_has_api_key(self):
        """测试 API Key 检查"""
        from src.config import AppConfig
        
        config = AppConfig()
        
        # 测试不存在的提供商
        assert config.has_api_key("nonexistent") == False
    
    def test_config_chapter_chars(self):
        """测试章节字数配置"""
        from src.config import AppConfig
        
        config = AppConfig()
        
        # 标准模式
        assert config.get_chapter_min_chars("standard") == 3500
        assert config.get_chapter_max_chars("standard") == 5500
        
        # 番茄模式
        assert config.get_chapter_min_chars("tomato") == 2100
        assert config.get_chapter_max_chars("tomato") == 2600


class TestGetConfig:
    """get_config 测试"""
    
    def test_get_config_singleton(self):
        """测试单例模式"""
        from src.config import get_config
        
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
