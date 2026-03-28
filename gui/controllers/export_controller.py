"""
导出控制器模块 (PySide6 版本)

处理导出相关的 GUI 操作。
"""

from typing import Dict, Optional
from PySide6.QtCore import Signal

from gui.controllers.base_controller import BaseController
from src.services.export_service import ExportService
from src.exceptions import ExportFailedError, ExportFormatNotSupportedError


class ExportController(BaseController):
    """导出控制器"""
    
    export_started = Signal(str)
    export_finished = Signal(str, str)
    export_failed = Signal(str)
    
    SUPPORTED_FORMATS = ["txt", "word", "epub"]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._export_service: Optional[ExportService] = None
        self._current_project: Optional[str] = None
        self._is_exporting = False
    
    def set_project(self, project_name: str) -> None:
        """设置当前项目"""
        self._current_project = project_name
        self._export_service = ExportService(project_name)
    
    def is_exporting(self) -> bool:
        """检查是否正在导出"""
        return self._is_exporting
    
    def export_txt(self, project_name: str, output_path: Optional[str] = None) -> Optional[str]:
        """导出为 TXT 格式"""
        return self._do_export(project_name, "txt", output_path)
    
    def export_word(self, project_name: str, output_path: Optional[str] = None) -> Optional[str]:
        """导出为 Word 格式"""
        return self._do_export(project_name, "word", output_path)
    
    def export_epub(self, project_name: str, output_path: Optional[str] = None) -> Optional[str]:
        """导出为 EPUB 格式"""
        return self._do_export(project_name, "epub", output_path)
    
    def export_all(self, project_name: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """导出所有格式"""
        self.set_project(project_name)
        
        if not self._export_service:
            return {}
        
        self._is_exporting = True
        results = {}
        
        for fmt in self.SUPPORTED_FORMATS:
            path = self._do_export(project_name, fmt, None)
            if path:
                results[fmt] = path
        
        self._is_exporting = False
        return results
    
    def _do_export(self, project_name: str, format: str, output_path: Optional[str]) -> Optional[str]:
        """执行导出"""
        if self._is_exporting and self._current_project != project_name:
            self.warning("已有导出任务正在进行中")
            return None
        
        self.set_project(project_name)
        
        if not self._export_service:
            return None
        
        self._is_exporting = True
        self.export_started.emit(format)
        self.info(f"开始导出 {format.upper()} 格式...")
        
        try:
            path = self._export_service.export(format, output_path)
            self.export_finished.emit(path, format)
            self.success(f"导出成功: {path}")
            return path
            
        except ExportFormatNotSupportedError as e:
            self.export_failed.emit(str(e))
            self.warning(str(e))
            return None
            
        except ExportFailedError as e:
            self.export_failed.emit(str(e))
            self.error(str(e))
            return None
            
        except Exception as e:
            message = f"导出失败: {str(e)}"
            self.export_failed.emit(message)
            self.handle_exception(e, "导出失败")
            return None
            
        finally:
            self._is_exporting = False
    
    def get_supported_formats(self) -> list:
        """获取支持的导出格式"""
        return self.SUPPORTED_FORMATS
