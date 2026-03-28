"""
导出服务模块

封装导出相关的业务逻辑：
1. 导出为 TXT
2. 导出为 Word
3. 导出为 EPUB
4. 批量导出所有格式
"""

import os
from typing import Optional, Dict
from datetime import datetime

from src.export import (
    export_to_txt,
    export_to_word,
    export_to_epub,
    export_all_formats,
)
from src.exceptions import (
    ProjectNotFoundError,
    ExportFailedError,
    ExportFormatNotSupportedError,
)


class ExportService:
    """
    导出服务
    
    封装导出的所有操作，提供统一的业务接口。
    
    使用示例:
        service = ExportService("我的小说")
        
        # 导出为 TXT
        path = service.to_txt()
        
        # 导出为 Word
        path = service.to_word()
        
        # 导出为 EPUB
        path = service.to_epub()
        
        # 导出所有格式
        paths = service.to_all()
    """
    
    SUPPORTED_FORMATS = ["txt", "word", "epub"]
    
    def __init__(self, project_name: str):
        """
        初始化导出服务
        
        参数:
            project_name: 项目名称
        """
        self.project_name = project_name
    
    def _validate_project(self) -> None:
        """验证项目是否存在"""
        from src.services.project_service import ProjectService
        if not ProjectService().exists(self.project_name):
            raise ProjectNotFoundError(self.project_name)
    
    def to_txt(self, output_path: Optional[str] = None) -> str:
        """
        导出为 TXT 格式
        
        参数:
            output_path: 输出路径（可选，默认自动生成）
        
        返回:
            导出文件路径
        
        异常:
            ProjectNotFoundError: 项目不存在
            ExportFailedError: 导出失败
        """
        self._validate_project()
        
        try:
            path = export_to_txt(self.project_name, output_path)
            return path
        except ImportError as e:
            raise ExportFailedError(
                self.project_name,
                "txt",
                f"缺少依赖库: {e}"
            ) from e
        except Exception as e:
            raise ExportFailedError(
                self.project_name,
                "txt",
                str(e)
            ) from e
    
    def to_word(self, output_path: Optional[str] = None) -> str:
        """
        导出为 Word 格式
        
        参数:
            output_path: 输出路径（可选）
        
        返回:
            导出文件路径
        
        异常:
            ProjectNotFoundError: 项目不存在
            ExportFailedError: 导出失败
        """
        self._validate_project()
        
        try:
            path = export_to_word(self.project_name, output_path)
            return path
        except ImportError as e:
            raise ExportFailedError(
                self.project_name,
                "word",
                f"缺少依赖库: python-docx。请运行: pip install python-docx"
            ) from e
        except Exception as e:
            raise ExportFailedError(
                self.project_name,
                "word",
                str(e)
            ) from e
    
    def to_epub(self, output_path: Optional[str] = None) -> str:
        """
        导出为 EPUB 格式
        
        参数:
            output_path: 输出路径（可选）
        
        返回:
            导出文件路径
        
        异常:
            ProjectNotFoundError: 项目不存在
            ExportFailedError: 导出失败
        """
        self._validate_project()
        
        try:
            path = export_to_epub(self.project_name, output_path)
            return path
        except ImportError as e:
            raise ExportFailedError(
                self.project_name,
                "epub",
                f"缺少依赖库: ebooklib。请运行: pip install ebooklib"
            ) from e
        except Exception as e:
            raise ExportFailedError(
                self.project_name,
                "epub",
                str(e)
            ) from e
    
    def to_all(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        导出所有格式
        
        参数:
            output_dir: 输出目录（可选）
        
        返回:
            格式到文件路径的映射 {"txt": path, "word": path, "epub": path}
        
        异常:
            ProjectNotFoundError: 项目不存在
            ExportFailedError: 导出失败
        """
        self._validate_project()
        
        try:
            paths = export_all_formats(self.project_name, output_dir)
            return paths
        except Exception as e:
            raise ExportFailedError(
                self.project_name,
                "all",
                str(e)
            ) from e
    
    def export(self, format: str, output_path: Optional[str] = None) -> str:
        """
        通用导出方法
        
        参数:
            format: 导出格式（txt/word/epub）
            output_path: 输出路径（可选）
        
        返回:
            导出文件路径
        
        异常:
            ExportFormatNotSupportedError: 不支持的格式
        """
        format = format.lower()
        
        if format == "txt":
            return self.to_txt(output_path)
        elif format in ("word", "docx"):
            return self.to_word(output_path)
        elif format == "epub":
            return self.to_epub(output_path)
        else:
            raise ExportFormatNotSupportedError(format)
    
    def get_default_output_dir(self) -> str:
        """
        获取默认导出目录
        
        返回:
            默认导出目录路径
        """
        from src.workspace import workspace_manager
        return os.path.join(
            workspace_manager.get_projects_dir(),
            self.project_name,
            "export"
        )
    
    def get_default_filename(self, format: str) -> str:
        """
        获取默认导出文件名
        
        参数:
            format: 导出格式
        
        返回:
            默认文件名
        """
        date_str = datetime.now().strftime("%Y%m%d")
        
        extensions = {
            "txt": ".txt",
            "word": ".docx",
            "epub": ".epub",
        }
        
        ext = extensions.get(format.lower(), ".txt")
        return f"{self.project_name}_{date_str}{ext}"
