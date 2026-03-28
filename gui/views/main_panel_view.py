"""
主面板视图组件
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import WelcomeWidget, apply_drop_shadow


class MainPanelView(QWidget):
    """
    主面板视图 - 包含欢迎页、仪表板和各个功能标签页
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainPanel")
        self._build_ui()
    
    def _build_ui(self):
        self.main_stack = QStackedWidget()
        
        self.welcome_widget = WelcomeWidget()
        self.main_stack.addWidget(self.welcome_widget)
        
        dashboard = self._build_dashboard()
        self.main_stack.addWidget(dashboard)
        
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(self.main_stack)
    
    def _build_dashboard(self):
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(24, 16, 36, 16)
        layout.setSpacing(12)
        
        layout.addLayout(self._build_header())
        layout.addWidget(self._build_stats())
        layout.addWidget(self._build_tabs(), 1)
        
        return dashboard
    
    def _build_header(self):
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_toggle_sidebar = QPushButton("☰")
        self.btn_toggle_sidebar.setObjectName("IconButton")
        self.btn_toggle_sidebar.setFixedSize(28, 28)
        self.btn_toggle_sidebar.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_sidebar.setVisible(False)
        header_layout.addWidget(self.btn_toggle_sidebar)
        
        header_layout.addSpacing(16)
        
        self.project_title = QLabel("欢迎使用")
        self.project_title.setObjectName("PageTitle")
        header_layout.addWidget(self.project_title)
        header_layout.addStretch(1)
        
        return header_layout
    
    def _build_stats(self):
        self.stats_widget = QWidget()
        self.stats_layout = QGridLayout(self.stats_widget)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setHorizontalSpacing(20)
        self.stats_layout.setVerticalSpacing(20)
        
        self.stat_cards = []
        self._stat_values = []
        stat_labels = ["已生成章节", "总字数", "平均字数/章", "预计总章数"]
        bar_colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]
        
        for i, text in enumerate(stat_labels):
            card_wrapper, value = self._build_stat_card(text, bar_colors[i % len(bar_colors)])
            self.stat_cards.append(card_wrapper)
            self._stat_values.append(value)
            self.stats_layout.addWidget(card_wrapper, 0, i)
        
        return self.stats_widget
    
    def _build_stat_card(self, label_text, color):
        card_wrapper = QFrame()
        card_wrapper.setObjectName("Card")
        
        wrapper_layout = QVBoxLayout(card_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)
        
        color_bar = QFrame()
        color_bar.setObjectName("ColorBar")
        color_bar.setFixedHeight(6)
        color_bar.setStyleSheet(f"background: {color}; border-top-left-radius: 14px; border-top-right-radius: 14px;")
        wrapper_layout.addWidget(color_bar)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(2)
        
        value = QLabel("0")
        value.setAlignment(Qt.AlignCenter)
        value.setObjectName("StatValue")
        value.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("StatLabel")
        label.setStyleSheet("font-size: 12px; color: #64748b;")
        
        content_layout.addWidget(value)
        content_layout.addWidget(label)
        
        wrapper_layout.addLayout(content_layout)
        
        apply_drop_shadow(card_wrapper, blur_radius=20, y_offset=4, alpha=15)
        
        return card_wrapper, value
    
    def _build_tabs(self):
        self.tabs = QTabWidget()
        return self.tabs
    
    def add_tab(self, widget, title):
        self.tabs.addTab(widget, title)
    
    def show_welcome(self):
        self.main_stack.setCurrentIndex(0)
    
    def show_dashboard(self):
        self.main_stack.setCurrentIndex(1)
    
    def get_stat_card(self, index):
        return self._stat_values[index]
