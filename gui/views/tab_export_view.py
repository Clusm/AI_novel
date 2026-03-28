"""
导出发布 Tab 视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import apply_drop_shadow


class TabExportView(QWidget):
    """
    导出发布标签页 - 包含各种导出格式按钮
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 14, 4, 4)
        
        card = QFrame()
        card.setObjectName("Card")
        apply_drop_shadow(card, blur_radius=20, y_offset=4, alpha=15)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)
        
        card_layout.addWidget(QLabel("📤 导出作品"))
        
        row = QHBoxLayout()
        row.setSpacing(16)
        
        self.btn_export_word = QPushButton("Word (.docx)")
        self.btn_export_epub = QPushButton("EPUB 电子书")
        self.btn_export_txt = QPushButton("纯文本 (.txt)")
        self.btn_export_all = QPushButton("全部导出")
        self.btn_export_all.setObjectName("PrimaryButton")
        
        for btn in [self.btn_export_word, self.btn_export_epub, self.btn_export_txt, self.btn_export_all]:
            btn.setMinimumHeight(44)
        
        row.addWidget(self.btn_export_word)
        row.addWidget(self.btn_export_epub)
        row.addWidget(self.btn_export_txt)
        row.addWidget(self.btn_export_all)
        card_layout.addLayout(row)
        
        self.export_result = QLabel("")
        self.export_result.setObjectName("Banner")
        self.export_result.setProperty("tone", "info")
        self.export_result.setWordWrap(True)
        self.export_result.setVisible(False)
        card_layout.addWidget(self.export_result)
        
        card_layout.addStretch(1)
        layout.addWidget(card)
        layout.addStretch(1)
    
    def show_result(self, message, tone="info"):
        self.export_result.setText(message)
        self.export_result.setProperty("tone", tone)
        self.export_result.style().unpolish(self.export_result)
        self.export_result.style().polish(self.export_result)
        self.export_result.setVisible(True)
    
    def hide_result(self):
        self.export_result.setVisible(False)
