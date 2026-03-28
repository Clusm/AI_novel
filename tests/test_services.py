"""
服务层测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestProjectService:
    """ProjectService 测试"""
    
    def test_service_creation(self):
        """测试服务创建"""
        from src.services.project_service import ProjectService
        
        service = ProjectService()
        
        assert service is not None
    
    @patch('src.services.project_service.get_all_projects')
    def test_get_all(self, mock_get_all):
        """测试获取所有项目"""
        from src.services.project_service import ProjectService
        
        mock_get_all.return_value = ["项目1", "项目2"]
        
        service = ProjectService()
        projects = service.get_all()
        
        assert len(projects) == 2
        assert "项目1" in projects
    
    @patch('src.services.project_service.get_all_projects')
    def test_exists(self, mock_get_all):
        """测试项目存在检查"""
        from src.services.project_service import ProjectService
        
        mock_get_all.return_value = ["项目1", "项目2"]
        
        service = ProjectService()
        
        assert service.exists("项目1") == True
        assert service.exists("项目3") == False
    
    @patch('src.services.project_service.get_all_projects')
    def test_project_not_found(self, mock_get_all):
        """测试项目不存在异常"""
        from src.services.project_service import ProjectService
        from src.exceptions import ProjectNotFoundError
        
        mock_get_all.return_value = []
        
        service = ProjectService()
        
        with pytest.raises(ProjectNotFoundError):
            service.get_info("不存在的项目")


class TestChapterService:
    """ChapterService 测试"""
    
    def test_service_creation(self):
        """测试服务创建"""
        from src.services.chapter_service import ChapterService
        
        service = ChapterService("测试项目")
        
        assert service.project_name == "测试项目"
    
    @patch('src.services.chapter_service.list_generated_chapters')
    def test_get_all(self, mock_list):
        """测试获取章节列表"""
        from src.services.chapter_service import ChapterService
        
        mock_list.return_value = ["第1章.md", "第2章.md"]
        
        service = ChapterService("测试项目")
        chapters = service.get_all()
        
        assert len(chapters) == 2
    
    def test_extract_number(self):
        """测试章节序号提取"""
        from src.services.chapter_service import ChapterService
        
        assert ChapterService._extract_number("第1章.md") == 1
        assert ChapterService._extract_number("第123章.md") == 123
        assert ChapterService._extract_number("invalid.md") == 0


class TestExportService:
    """ExportService 测试"""
    
    def test_service_creation(self):
        """测试服务创建"""
        from src.services.export_service import ExportService
        
        service = ExportService("测试项目")
        
        assert service.project_name == "测试项目"
    
    def test_supported_formats(self):
        """测试支持的格式"""
        from src.services.export_service import ExportService
        
        assert "txt" in ExportService.SUPPORTED_FORMATS
        assert "word" in ExportService.SUPPORTED_FORMATS
        assert "epub" in ExportService.SUPPORTED_FORMATS


class TestAPIService:
    """APIService 测试"""
    
    def test_service_creation(self):
        """测试服务创建"""
        from src.services.api_service import APIService
        
        service = APIService()
        
        assert service is not None
    
    def test_providers(self):
        """测试提供商列表"""
        from src.services.api_service import APIService
        
        providers = APIService.PROVIDERS
        
        assert "deepseek" in providers
        assert "qwen" in providers
        assert "kimi" in providers
    
    def test_get_all_providers(self):
        """测试获取所有提供商"""
        from src.services.api_service import APIService
        
        service = APIService()
        providers = service.get_all_providers()
        
        assert len(providers) == 3
    
    def test_validate_key_format(self):
        """测试 API Key 格式验证"""
        from src.services.api_service import APIService
        
        service = APIService()
        
        # DeepSeek
        valid, msg = service.validate_key_format("deepseek", "sk-test123")
        assert valid == True
        
        valid, msg = service.validate_key_format("deepseek", "invalid")
        assert valid == False
        
        # 空值
        valid, msg = service.validate_key_format("deepseek", "")
        assert valid == False
