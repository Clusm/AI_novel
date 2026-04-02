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
        layout.setContentsMargins(24, 8, 24, 16)
        layout.setSpacing(8)

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
        self.stats_layout.setHorizontalSpacing(12)
        self.stats_layout.setVerticalSpacing(12)
        
        self.stat_cards = []
        self._stat_values = []
        stat_labels = ["已生成章节", "总字数", "平均字数/章", "预计总章数"]

        # 使用新的配色方案
        from gui.styles import Colors
        card_configs = [
            {"bg": Colors.STAT_CARD_CHAPTERS_BG, "text": Colors.STAT_CARD_CHAPTERS_TEXT, "icon": "📚"},
            {"bg": Colors.STAT_CARD_WORDS_BG, "text": Colors.STAT_CARD_WORDS_TEXT, "icon": "✍️"},
            {"bg": Colors.STAT_CARD_AVG_BG, "text": Colors.STAT_CARD_AVG_TEXT, "icon": "📊"},
            {"bg": Colors.STAT_CARD_TOTAL_BG, "text": Colors.STAT_CARD_TOTAL_TEXT, "icon": "🎯"},
        ]

        for i, text in enumerate(stat_labels):
            card_wrapper, value = self._build_stat_card(text, card_configs[i])
            self.stat_cards.append(card_wrapper)
            self._stat_values.append(value)
            self.stats_layout.addWidget(card_wrapper, 0, i)
        
        return self.stats_widget
    
    def _build_stat_card(self, label_text, config):
        card_wrapper = QFrame()
        card_wrapper.setObjectName("Card")
        card_wrapper.setStyleSheet(f"""
            QFrame#Card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {config['bg']}, stop:1 #FFFFFF);
                border: 1px solid rgba(0,0,0,0.04);
                border-radius: 10px;
            }}
        """)

        wrapper_layout = QVBoxLayout(card_wrapper)
        wrapper_layout.setContentsMargins(12, 12, 12, 12)
        wrapper_layout.setSpacing(4)

        # 图标
        icon_label = QLabel(config['icon'])
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px;")
        wrapper_layout.addWidget(icon_label)

        # 数值
        value = QLabel("0")
        value.setAlignment(Qt.AlignCenter)
        value.setObjectName("StatValue")
        value.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {config['text']};")
        wrapper_layout.addWidget(value)

        # 标签
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignCenter)
        label.setObjectName("StatLabel")
        label.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 500;")
        wrapper_layout.addWidget(label)

        apply_drop_shadow(card_wrapper, blur_radius=15, y_offset=2, alpha=12)

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
