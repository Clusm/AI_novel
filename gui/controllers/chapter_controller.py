"""
章节控制器模块 (PySide6 版本)

处理章节相关的 GUI 操作。
"""

from typing import List, Optional, Callable
from PySide6.QtCore import Signal

from gui.controllers.base_controller import BaseController
from src.services.chapter_service import ChapterService, ChapterInfo
from src.exceptions import ProjectNotFoundError, ChapterNotFoundError


class ChapterController(BaseController):
    """章节控制器"""
    
    generation_started = Signal()
    generation_progress = Signal(int, int, str)
    generation_finished = Signal(bool, str)
    chapter_generated = Signal(int)
    chapters_loaded = Signal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._chapter_service: Optional[ChapterService] = None
        self._is_generating = False
        self._current_project: Optional[str] = None
    
    def set_project(self, project_name: str) -> None:
        """设置当前项目"""
        self._current_project = project_name
        self._chapter_service = ChapterService(project_name)
    
    def get_chapters(self) -> List[str]:
        """获取章节列表"""
        if not self._chapter_service:
            return []
        
        chapters = self._chapter_service.get_all()
        self.chapters_loaded.emit(chapters)
        return chapters
    
    def get_chapter(self, chapter_file: str) -> str:
        """获取章节内容"""
        if not self._chapter_service:
            return ""
        
        try:
            return self._chapter_service.get(chapter_file)
        except ChapterNotFoundError:
            self.warning(f"章节 {chapter_file} 不存在")
            return ""
    
    def is_generating(self) -> bool:
        """检查是否正在生成"""
        return self._is_generating
    
    def get_total_word_count(self) -> int:
        """获取总字数"""
        if not self._chapter_service:
            return 0
        return self._chapter_service.get_total_word_count()
    
    def get_next_chapter_number(self) -> int:
        """获取下一个章节序号"""
        if not self._chapter_service:
            return 1
        return self._chapter_service.get_next_chapter_number()
    
    def chapter_exists(self, chapter_number: int) -> bool:
        """检查章节是否存在"""
        if not self._chapter_service:
            return False
        return self._chapter_service.exists(chapter_number)
