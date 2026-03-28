"""
异常模块测试
"""

import pytest


class TestNovelWriterError:
    """NovelWriterError 测试"""
    
    def test_basic_error(self):
        """测试基本异常"""
        from src.exceptions import NovelWriterError
        
        error = NovelWriterError("测试错误")
        
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.code == "UNKNOWN_ERROR"
    
    def test_error_with_code(self):
        """测试带代码的异常"""
        from src.exceptions import NovelWriterError
        
        error = NovelWriterError("测试错误", code="TEST_ERROR")
        
        assert "[TEST_ERROR]" in str(error)
        assert error.code == "TEST_ERROR"
    
    def test_error_to_dict(self):
        """测试转换为字典"""
        from src.exceptions import NovelWriterError
        
        error = NovelWriterError("测试错误", code="TEST_ERROR", details={"key": "value"})
        
        result = error.to_dict()
        
        assert result["error"] == "TEST_ERROR"
        assert result["message"] == "测试错误"
        assert result["details"]["key"] == "value"


class TestAPIExceptions:
    """API 异常测试"""
    
    def test_api_key_missing(self):
        """测试 API Key 缺失异常"""
        from src.exceptions import APIKeyMissingError
        
        error = APIKeyMissingError("deepseek")
        
        assert "deepseek" in str(error)
        assert error.code == "API_KEY_MISSING"
        assert error.details["provider"] == "deepseek"
    
    def test_api_connection_error(self):
        """测试 API 连接错误"""
        from src.exceptions import APIConnectionError
        
        error = APIConnectionError("qwen", "网络超时")
        
        assert "qwen" in str(error)
        assert "网络超时" in str(error)
        assert error.code == "API_CONNECTION_ERROR"


class TestProjectExceptions:
    """项目异常测试"""
    
    def test_project_not_found(self):
        """测试项目不存在异常"""
        from src.exceptions import ProjectNotFoundError
        
        error = ProjectNotFoundError("我的小说")
        
        assert "我的小说" in str(error)
        assert error.code == "PROJECT_NOT_FOUND"
    
    def test_project_already_exists(self):
        """测试项目已存在异常"""
        from src.exceptions import ProjectAlreadyExistsError
        
        error = ProjectAlreadyExistsError("我的小说")
        
        assert "已存在" in str(error)
        assert error.code == "PROJECT_ALREADY_EXISTS"


class TestChapterExceptions:
    """章节异常测试"""
    
    def test_chapter_generation_error(self):
        """测试章节生成失败异常"""
        from src.exceptions import ChapterGenerationError
        
        error = ChapterGenerationError("我的小说", 1, "API 调用失败")
        
        assert "我的小说" in str(error)
        assert "第1章" in str(error)
        assert error.code == "CHAPTER_GENERATION_ERROR"
    
    def test_generation_timeout_error(self):
        """测试生成超时异常"""
        from src.exceptions import GenerationTimeoutError
        
        error = GenerationTimeoutError("我的小说", 1, 600)
        
        assert "超时" in str(error)
        assert "600" in str(error)


class TestExportExceptions:
    """导出异常测试"""
    
    def test_export_format_not_supported(self):
        """测试不支持的导出格式异常"""
        from src.exceptions import ExportFormatNotSupportedError
        
        error = ExportFormatNotSupportedError("pdf")
        
        assert "pdf" in str(error)
        assert error.code == "EXPORT_FORMAT_NOT_SUPPORTED"
    
    def test_export_failed(self):
        """测试导出失败异常"""
        from src.exceptions import ExportFailedError
        
        error = ExportFailedError("我的小说", "word", "权限不足")
        
        assert "我的小说" in str(error)
        assert "word" in str(error)
        assert "权限不足" in str(error)


class TestLicenseExceptions:
    """授权异常测试"""
    
    def test_license_invalid(self):
        """测试授权码无效异常"""
        from src.exceptions import LicenseInvalidError
        
        error = LicenseInvalidError("格式错误")
        
        assert "无效" in str(error)
        assert error.code == "LICENSE_INVALID"
    
    def test_license_expired(self):
        """测试授权过期异常"""
        from src.exceptions import LicenseExpiredError
        
        error = LicenseExpiredError("2024-12-31")
        
        assert "2024-12-31" in str(error)
        assert error.code == "LICENSE_EXPIRED"


class TestWrapException:
    """wrap_exception 测试"""
    
    def test_wrap_exception(self):
        """测试异常包装"""
        from src.exceptions import (
            wrap_exception,
            NovelWriterError,
            APIKeyMissingError,
        )
        
        original = ValueError("原始错误")
        
        wrapped = wrap_exception(
            original,
            APIKeyMissingError,
            message="自定义消息",
            provider="deepseek",
        )
        
        assert isinstance(wrapped, NovelWriterError)
        assert wrapped.cause == original
        assert "自定义消息" in str(wrapped)
