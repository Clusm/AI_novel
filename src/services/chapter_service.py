"""
章节服务模块

封装章节相关的业务逻辑：
1. 章节生成（单章/批量）
2. 章节读取
3. 章节摘要和事实台账
4. 生成进度回调
"""

from typing import List, Optional, Callable
from dataclasses import dataclass

from src.project import (
    load_chapter,
    save_chapter,
    load_chapter_summary,
    save_chapter_summary,
    load_recent_canon_entries,
    save_canon_entry,
)
from src.generator import generate_chapter, generate_multiple_chapters
from src.exceptions import (
    ProjectNotFoundError,
    ChapterNotFoundError,
    ChapterGenerationError,
    GenerationTimeoutError,
)


@dataclass
class ChapterInfo:
    """章节信息数据类"""
    number: int
    file_name: str
    word_count: int
    has_summary: bool = False
    has_canon: bool = False


class ChapterService:
    """
    章节服务
    
    封装章节的所有操作，提供统一的业务接口。
    
    使用示例:
        service = ChapterService("我的小说")
        
        # 生成章节
        content = service.generate(1, outline, log_callback=my_callback)
        
        # 获取章节列表
        chapters = service.get_all()
        
        # 读取章节
        content = service.get("第1章.md")
    """
    
    def __init__(self, project_name: str):
        """
        初始化章节服务
        
        参数:
            project_name: 项目名称
        """
        self.project_name = project_name
    
    def _validate_project(self) -> None:
        """验证项目是否存在"""
        from src.services.project_service import ProjectService
        if not ProjectService().exists(self.project_name):
            raise ProjectNotFoundError(self.project_name)
    
    def generate(
        self,
        chapter_number: int,
        outline: str,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ) -> str:
        """
        生成单个章节
        
        参数:
            chapter_number: 章节序号
            outline: 故事大纲
            log_callback: 日志回调函数 (message, status)
        
        返回:
            生成的章节内容
        
        异常:
            ProjectNotFoundError: 项目不存在
            ChapterGenerationError: 生成失败
        """
        self._validate_project()
        
        try:
            content = generate_chapter(
                self.project_name,
                outline,
                chapter_number,
                log_callback=log_callback,
            )
            return content
        except Exception as e:
            raise ChapterGenerationError(
                self.project_name,
                chapter_number,
                str(e),
                cause=e,
            ) from e
    
    def generate_batch(
        self,
        start: int,
        count: int,
        outline: str,
        log_callback: Optional[Callable[[str, str], None]] = None,
    ) -> List[str]:
        """
        批量生成章节
        
        参数:
            start: 起始章节序号
            count: 生成数量
            outline: 故事大纲
            log_callback: 日志回调函数
        
        返回:
            生成的章节内容列表
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        self._validate_project()
        
        end = start + count - 1
        results = generate_multiple_chapters(
            self.project_name,
            outline,
            start,
            end,
            log_callback=log_callback,
        )
        return results
    
    def get_all(self) -> List[str]:
        """
        获取所有已生成的章节文件名
        
        返回:
            章节文件名列表（如 ["第1章.md", "第2章.md"]）
        """
        from src.project import list_generated_chapters
        return list_generated_chapters(self.project_name)
    
    def get(self, chapter_file: str) -> str:
        """
        读取章节内容
        
        参数:
            chapter_file: 章节文件名（如 "第1章.md"）
        
        返回:
            章节内容
        
        异常:
            ChapterNotFoundError: 章节不存在
        """
        content = load_chapter(self.project_name, chapter_file)
        if not content:
            raise ChapterNotFoundError(self.project_name, self._extract_number(chapter_file))
        return content
    
    def get_by_number(self, chapter_number: int) -> str:
        """
        按序号读取章节内容
        
        参数:
            chapter_number: 章节序号
        
        返回:
            章节内容
        
        异常:
            ChapterNotFoundError: 章节不存在
        """
        chapter_file = f"第{chapter_number}章.md"
        return self.get(chapter_file)
    
    def save(self, chapter_number: int, content: str) -> None:
        """
        保存章节内容
        
        参数:
            chapter_number: 章节序号
            content: 章节内容
        """
        save_chapter(self.project_name, chapter_number, content)
    
    def get_summary(self, chapter_number: int) -> str:
        """
        获取章节摘要
        
        参数:
            chapter_number: 章节序号
        
        返回:
            摘要内容（可能为空字符串）
        """
        return load_chapter_summary(self.project_name, chapter_number)
    
    def save_summary(self, chapter_number: int, summary: str) -> None:
        """
        保存章节摘要
        
        参数:
            chapter_number: 章节序号
            summary: 摘要内容
        """
        save_chapter_summary(self.project_name, chapter_number, summary)
    
    def get_canon_entries(self, limit: int = 3) -> List[str]:
        """
        获取最近的事实台账
        
        参数:
            limit: 获取数量
        
        返回:
            事实台账内容列表
        """
        return load_recent_canon_entries(self.project_name, limit)
    
    def save_canon(self, chapter_number: int, canon: str) -> None:
        """
        保存事实台账
        
        参数:
            chapter_number: 章节序号
            canon: 事实台账内容
        """
        save_canon_entry(self.project_name, chapter_number, canon)
    
    def get_info(self, chapter_file: str) -> ChapterInfo:
        """
        获取章节信息
        
        参数:
            chapter_file: 章节文件名
        
        返回:
            章节信息
        """
        content = load_chapter(self.project_name, chapter_file)
        number = self._extract_number(chapter_file)
        
        return ChapterInfo(
            number=number,
            file_name=chapter_file,
            word_count=len(content) if content else 0,
            has_summary=bool(load_chapter_summary(self.project_name, number)),
            has_canon=bool(load_recent_canon_entries(self.project_name, 1)),
        )
    
    def get_word_count(self, chapter_file: str) -> int:
        """
        获取章节字数
        
        参数:
            chapter_file: 章节文件名
        
        返回:
            字数
        """
        content = load_chapter(self.project_name, chapter_file)
        return len(content) if content else 0
    
    def get_total_word_count(self) -> int:
        """
        获取项目总字数
        
        返回:
            总字数
        """
        total = 0
        for chapter_file in self.get_all():
            total += self.get_word_count(chapter_file)
        return total
    
    def exists(self, chapter_number: int) -> bool:
        """
        检查章节是否存在
        
        参数:
            chapter_number: 章节序号
        
        返回:
            是否存在
        """
        chapter_file = f"第{chapter_number}章.md"
        return chapter_file in self.get_all()
    
    def get_next_chapter_number(self) -> int:
        """
        获取下一个章节序号
        
        返回:
            下一个章节序号
        """
        chapters = self.get_all()
        if not chapters:
            return 1
        
        max_num = 0
        for chapter_file in chapters:
            num = self._extract_number(chapter_file)
            if num > max_num:
                max_num = num
        
        return max_num + 1
    
    @staticmethod
    def _extract_number(chapter_file: str) -> int:
        """从文件名提取章节序号"""
        import re
        match = re.search(r"(\d+)", chapter_file)
        return int(match.group(1)) if match else 0
