"""
运行监控 Tab 视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import apply_drop_shadow


class TabMonitorView(QWidget):
    """
    运行监控标签页 - 包含 Agent 思维流和终端命令行视图
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
    
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 14, 4, 4)
        layout.setSpacing(20)
        
        logs = QFrame()
        logs.setObjectName("Card")
        apply_drop_shadow(logs, blur_radius=20, y_offset=4, alpha=15)
        
        logs_layout = QVBoxLayout(logs)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        
        logs_layout.addWidget(self._build_header())
        logs_layout.addWidget(self._build_content(), 1)
        
        layout.addWidget(logs)
    
    def _build_header(self):
        header = QFrame()
        header.setStyleSheet("border-bottom: 1px solid #e2e8f0; background: #f8fafc; border-top-left-radius: 16px; border-top-right-radius: 16px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 8, 16, 8)
        h_layout.setSpacing(8)
        
        self.btn_mode_thought = QPushButton("Agent思维流")
        self.btn_mode_terminal = QPushButton("终端命令行")
        self.btn_mode_thought.setCheckable(True)
        self.btn_mode_terminal.setCheckable(True)
        self.btn_mode_thought.setChecked(True)
        self.btn_mode_thought.setCursor(Qt.PointingHandCursor)
        self.btn_mode_terminal.setCursor(Qt.PointingHandCursor)
        
        toggle_style = """
            QPushButton {
                background: transparent;
                border: none;
                color: #64748b;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 14px;
                border-radius: 6px;
            }
            QPushButton:checked {
                background: #ffffff;
                color: #3b82f6;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
            }
            QPushButton:hover:!checked {
                background: rgba(255, 255, 255, 0.5);
                color: #475569;
            }
        """
        self.btn_mode_thought.setStyleSheet(toggle_style)
        self.btn_mode_terminal.setStyleSheet(toggle_style)
        
        self.monitor_mode_group = QButtonGroup(self)
        self.monitor_mode_group.addButton(self.btn_mode_thought, 0)
        self.monitor_mode_group.addButton(self.btn_mode_terminal, 1)
        
        h_layout.addWidget(self.btn_mode_thought)
        h_layout.addWidget(self.btn_mode_terminal)
        h_layout.addStretch(1)
        
        self.btn_refresh_logs = QPushButton("🔄")
        self.btn_refresh_logs.setFixedSize(32, 28)
        self.btn_refresh_logs.setCursor(Qt.PointingHandCursor)
        self.btn_refresh_logs.setToolTip("刷新")
        self.btn_refresh_logs.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                color: #64748b;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #e2e8f0;
                color: #475569;
            }
            QPushButton:pressed {
                background: #cbd5e1;
            }
        """)
        
        self.btn_clear_logs = QPushButton("🗑️")
        self.btn_clear_logs.setFixedSize(32, 28)
        self.btn_clear_logs.setCursor(Qt.PointingHandCursor)
        self.btn_clear_logs.setToolTip("清空")
        self.btn_clear_logs.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                color: #64748b;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #fee2e2;
                color: #dc2626;
            }
            QPushButton:pressed {
                background: #fecaca;
            }
        """)
        
        h_layout.addWidget(self.btn_refresh_logs)
        h_layout.addWidget(self.btn_clear_logs)
        
        return header
    
    def _build_content(self):
        self.monitor_stack = QStackedWidget()
        
        self.monitor_stack.addWidget(self._build_thought_view())
        self.monitor_stack.addWidget(self._build_raw_view())
        
        return self.monitor_stack
    
    def _build_thought_view(self):
        thought_tab = QWidget()
        thought_layout = QVBoxLayout(thought_tab)
        thought_layout.setContentsMargins(0, 0, 0, 0)
        thought_layout.setSpacing(0)
        
        self.logs_view = QTextEdit()
        self.logs_view.setObjectName("LogViewer")
        self.logs_view.setReadOnly(True)
        self.logs_view.setStyleSheet("""
            QTextEdit {
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 116, 139, 0.4);
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(100, 116, 139, 0.7);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        thought_layout.addWidget(self.logs_view, 1)
        
        return thought_tab
    
    def _build_raw_view(self):
        raw_tab = QWidget()
        raw_layout = QVBoxLayout(raw_tab)
        raw_layout.setContentsMargins(0, 0, 0, 0)
        raw_layout.setSpacing(0)
        
        self.raw_logs_view = QTextEdit()
        self.raw_logs_view.setReadOnly(True)
        self.raw_logs_view.document().setMaximumBlockCount(5000)
        self.raw_logs_view.setStyleSheet("""
            QTextEdit {
                border: none; 
                background: #1e1e1e; 
                padding: 12px;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.2);
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 0.4);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        raw_layout.addWidget(self.raw_logs_view, 1)
        
        return raw_tab
    
    def show_thought_view(self):
        self.monitor_stack.setCurrentIndex(0)
    
    def show_raw_view(self):
        self.monitor_stack.setCurrentIndex(1)
