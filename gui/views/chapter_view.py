"""
章节视图模块 (PySide6 版本)

显示章节列表和章节内容。
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QTextEdit,
    QSplitter, QMessageBox,
)
from PySide6.QtCore import Signal, Qt

from src.services.chapter_service import ChapterService, ChapterInfo


class ChapterView(QWidget):
    """
    章节视图
    
    显示章节列表和章节内容。
    
    信号:
        chapter_selected: 章节被选中 (chapter_file)
        generate_requested: 请求生成章节 (start_chapter, count)
    """
    
    chapter_selected = Signal(str)
    generate_requested = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._chapter_service: Optional[ChapterService] = None
        self._current_project: Optional[str] = None
        self._current_chapter: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("章节阅读")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self._word_count_label = QLabel("总字数: 0")
        self._word_count_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self._word_count_label)
        
        layout.addLayout(header_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self._chapter_list = QListWidget()
        self._chapter_list.setMinimumWidth(150)
        self._chapter_list.setMaximumWidth(250)
        self._chapter_list.itemClicked.connect(self._on_chapter_clicked)
        left_layout.addWidget(self._chapter_list)
        
        self._refresh_btn = QPushButton("刷新章节")
        self._refresh_btn.clicked.connect(self._refresh_chapters)
        left_layout.addWidget(self._refresh_btn)
        
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self._chapter_title = QLabel("请选择章节")
        self._chapter_title.setStyleSheet("font-size: 13px; font-weight: bold; padding: 5px;")
        right_layout.addWidget(self._chapter_title)
        
        self._content_edit = QTextEdit()
        self._content_edit.setReadOnly(True)
        self._content_edit.setPlaceholderText("章节内容将显示在这里...")
        right_layout.addWidget(self._content_edit)
        
        splitter.addWidget(right_widget)
        
        splitter.setSizes([200, 500])
        
        layout.addWidget(splitter)
    
    def set_project(self, project_name: str):
        """设置当前项目"""
        self._current_project = project_name
        self._chapter_service = ChapterService(project_name)
        self._refresh_chapters()
    
    def _refresh_chapters(self):
        """刷新章节列表"""
        if not self._chapter_service:
            return
        
        self._chapter_list.clear()
        chapters = self._chapter_service.get_all()
        
        for chapter_file in chapters:
            item = QListWidgetItem(chapter_file)
            self._chapter_list.addItem(item)
        
        total_words = self._chapter_service.get_total_word_count()
        self._word_count_label.setText(f"总字数: {total_words:,}")
    
    def _on_chapter_clicked(self, item: QListWidgetItem):
        """章节点击"""
        if not self._chapter_service:
            return
        
        chapter_file = item.text()
        self._current_chapter = chapter_file
        
        content = self._chapter_service.get(chapter_file)
        self._content_edit.setPlainText(content)
        self._chapter_title.setText(chapter_file.replace(".md", ""))
        
        self.chapter_selected.emit(chapter_file)
    
    def get_current_chapter(self) -> Optional[str]:
        """获取当前章节"""
        return self._current_chapter
    
    def get_service(self) -> Optional[ChapterService]:
        """获取服务"""
        return self._chapter_service
    
    def clear(self):
        """清空内容"""
        self._chapter_list.clear()
        self._content_edit.clear()
        self._chapter_title.setText("请选择章节")
        self._word_count_label.setText("总字数: 0")
