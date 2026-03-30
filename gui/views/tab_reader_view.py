"""
阅读管理 Tab 视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import apply_drop_shadow
from gui.styles import Colors, Typography


class TabReaderView(QWidget):
    """
    阅读管理标签页 - 包含章节列表和阅读器
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        tab_layout = QHBoxLayout(self)
        tab_layout.setContentsMargins(4, 14, 4, 4)
        tab_layout.setSpacing(20)
        
        tab_layout.addWidget(self._build_chapter_list(), 1)
        tab_layout.addWidget(self._build_reader(), 3)
    
    def _build_chapter_list(self):
        left = QFrame()
        left.setObjectName("Card")
        left.setMaximumWidth(320)
        apply_drop_shadow(left, blur_radius=20, y_offset=4, alpha=15)
        
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(12)
        
        left_layout.addWidget(QLabel("目录"))
        
        self.chapter_search = QLineEdit()
        self.chapter_search.setPlaceholderText("搜索章节...")
        self.chapter_search.setClearButtonEnabled(False)
        left_layout.addWidget(self.chapter_search)
        
        self.chapter_combo = QComboBox()
        left_layout.addWidget(self.chapter_combo)
        
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("上一章")
        self.btn_next = QPushButton("下一章")
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)
        left_layout.addLayout(nav)
        
        left_layout.addStretch(1)
        
        return left
    
    def _build_reader(self):
        right = QFrame()
        right.setObjectName("Card")
        apply_drop_shadow(right, blur_radius=20, y_offset=4, alpha=15)
        
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QFrame()
        header.setObjectName("CardHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        self.chapter_title = QLabel("暂无章节")
        self.chapter_title.setStyleSheet(f"font-size: 18px; font-weight: {Typography.WEIGHT_BOLD}; color: {Colors.TEXT_PRIMARY};")

        self.chapter_words = QLabel("0 字")
        self.chapter_words.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM};")

        self.btn_copy_chapter = QPushButton("📋 复制")
        self.btn_copy_chapter.setObjectName("SecondaryButton")
        self.btn_copy_chapter.setFixedSize(60, 28)
        self.btn_copy_chapter.setCursor(Qt.PointingHandCursor)
        
        header_layout.addWidget(self.chapter_title, 1)
        header_layout.addWidget(self.chapter_words)
        header_layout.addSpacing(12)
        header_layout.addWidget(self.btn_copy_chapter)
        right_layout.addWidget(header)
        
        self.chapter_content = QTextEdit()
        self.chapter_content.setObjectName("ReaderContent")
        self.chapter_content.setReadOnly(True)
        right_layout.addWidget(self.chapter_content, 1)
        
        return right
