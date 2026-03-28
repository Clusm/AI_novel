"""
GUI 控制器模块 (PySide6 版本)

提供 MVC/MVP 模式的控制器层，解耦 GUI 和业务逻辑。
"""

from gui.controllers.base_controller import BaseController
from gui.controllers.project_controller import ProjectController
from gui.controllers.chapter_controller import ChapterController
from gui.controllers.export_controller import ExportController

__all__ = [
    "BaseController",
    "ProjectController",
    "ChapterController",
    "ExportController",
]
