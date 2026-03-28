"""
项目控制器模块 (PySide6 版本)

处理项目相关的 GUI 操作。
"""

from typing import List, Optional
from PySide6.QtCore import Signal

from gui.controllers.base_controller import BaseController
from src.services.project_service import ProjectService, ProjectInfo
from src.exceptions import ProjectNotFoundError, ProjectAlreadyExistsError


class ProjectController(BaseController):
    """项目控制器"""
    
    projects_changed = Signal()
    project_loaded = Signal(str)
    project_created = Signal(str)
    project_deleted = Signal(str)
    project_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_service = ProjectService()
        self._current_project: Optional[str] = None
        self._projects: List[str] = []
    
    def load_projects(self) -> List[str]:
        """加载项目列表"""
        try:
            self._projects = self._project_service.get_all()
            self.projects_changed.emit()
            self.info(f"已加载 {len(self._projects)} 个项目")
            return self._projects
        except Exception as e:
            self.handle_exception(e, "加载项目列表失败")
            return []
    
    def get_projects(self) -> List[str]:
        """获取当前项目列表"""
        return self._projects
    
    def create_project(self, name: str, style: str = "standard") -> bool:
        """创建新项目"""
        try:
            created_name = self._project_service.create(name, style)
            self._projects.append(created_name)
            self.projects_changed.emit()
            self.project_created.emit(created_name)
            self.success(f"项目 '{created_name}' 创建成功")
            return True
        except ProjectAlreadyExistsError:
            self.warning(f"项目 '{name}' 已存在")
            return False
        except Exception as e:
            self.handle_exception(e, f"创建项目 '{name}' 失败")
            return False
    
    def delete_project(self, name: str) -> bool:
        """删除项目"""
        try:
            self._project_service.delete(name)
            if name in self._projects:
                self._projects.remove(name)
            if self._current_project == name:
                self._current_project = None
            self.projects_changed.emit()
            self.project_deleted.emit(name)
            self.success(f"项目 '{name}' 已删除")
            return True
        except ProjectNotFoundError:
            self.warning(f"项目 '{name}' 不存在")
            return False
        except Exception as e:
            self.handle_exception(e, f"删除项目 '{name}' 失败")
            return False
    
    def select_project(self, name: str) -> bool:
        """选择项目"""
        if not self._project_service.exists(name):
            self.warning(f"项目 '{name}' 不存在")
            return False
        
        self._current_project = name
        self.project_selected.emit(name)
        self.project_loaded.emit(name)
        self.info(f"已选择项目 '{name}'")
        return True
    
    def get_current_project(self) -> Optional[str]:
        """获取当前选中的项目"""
        return self._current_project
    
    def get_project_info(self, name: str) -> Optional[ProjectInfo]:
        """获取项目信息"""
        try:
            return self._project_service.get_info(name)
        except ProjectNotFoundError:
            return None
    
    def get_outline(self, name: str) -> str:
        """获取项目大纲"""
        return self._project_service.get_outline(name)
    
    def save_outline(self, name: str, outline: str) -> bool:
        """保存项目大纲"""
        try:
            self._project_service.save_outline(name, outline)
            self.success("大纲已保存")
            return True
        except Exception as e:
            self.handle_exception(e, "保存大纲失败")
            return False
    
    def project_exists(self, name: str) -> bool:
        """检查项目是否存在"""
        return self._project_service.exists(name)
