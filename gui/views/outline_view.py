"""
大纲视图模块 (PySide6 版本)

显示和编辑项目大纲。
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QMessageBox,
)
from PySide6.QtCore import Signal, Qt


class OutlineView(QWidget):
    """
    大纲视图
    
    显示和编辑项目大纲。
    
    信号:
        outline_saved: 大纲已保存
        generate_requested: 请求生成章节
    """
    
    outline_saved = Signal()
    generate_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_project: Optional[str] = None
        self._outline: str = ""
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("故事大纲")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self._char_count_label = QLabel("字数: 0")
        self._char_count_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self._char_count_label)
        
        layout.addLayout(header_layout)
        
        self._outline_edit = QTextEdit()
        self._outline_edit.setPlaceholderText(
            "请在此输入故事大纲...\n\n"
            "建议格式：\n"
            "1. 故事背景\n"
            "2. 主要人物\n"
            "3. 情节发展\n"
            "4. 章节规划"
        )
        self._outline_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._outline_edit)
        
        button_layout = QHBoxLayout()
        
        self._save_btn = QPushButton("保存大纲")
        self._save_btn.clicked.connect(self._save_outline)
        button_layout.addWidget(self._save_btn)
        
        self._load_btn = QPushButton("加载大纲")
        self._load_btn.clicked.connect(self._load_outline)
        button_layout.addWidget(self._load_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _on_text_changed(self):
        """文本变化"""
        text = self._outline_edit.toPlainText()
        self._outline = text
        self._char_count_label.setText(f"字数: {len(text)}")
    
    def set_project(self, project_name: str):
        """设置当前项目"""
        self._current_project = project_name
        self._load_outline()
    
    def _load_outline(self):
        """加载大纲"""
        if not self._current_project:
            return
        
        from src.services.project_service import ProjectService
        
        try:
            service = ProjectService()
            outline = service.get_outline(self._current_project)
            self._outline_edit.setPlainText(outline)
            self._outline = outline
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"加载大纲失败: {e}")
    
    def _save_outline(self):
        """保存大纲"""
        if not self._current_project:
            QMessageBox.warning(self, "保存失败", "请先选择项目")
            return
        
        from src.services.project_service import ProjectService
        
        try:
            service = ProjectService()
            service.save_outline(self._current_project, self._outline)
            self.outline_saved.emit()
            QMessageBox.information(self, "保存成功", "大纲已保存")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存大纲失败: {e}")
    
    def get_outline(self) -> str:
        """获取大纲内容"""
        return self._outline
    
    def clear(self):
        """清空内容"""
        self._outline_edit.clear()
        self._outline = ""
        self._current_project = None
