"""
侧边栏视图组件
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import DraggableHeader, apply_drop_shadow


class SidebarView(QFrame):
    """
    侧边栏视图 - 包含项目选择、文风设置、系统设置等
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setMinimumWidth(232)
        self.setMaximumWidth(420)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self._build_header())
        layout.addWidget(self._build_content())
    
    def _build_header(self):
        header = DraggableHeader(self.window() if self.parent() else None)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(12)
        
        logo = QLabel("✦✦")
        logo.setStyleSheet("font-size: 20px; color: #3b82f6; letter-spacing: 2px;")
        header_layout.addWidget(logo)
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        title = QLabel("AI_Novel_Writer")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #0f172a; padding: 0;")
        title_layout.addWidget(title)
        
        self.version_label = QLabel("v2.4")
        self.version_label.setObjectName("MutedText")
        self.version_label.setStyleSheet("padding: 0;")
        title_layout.addWidget(self.version_label)
        
        header_layout.addWidget(title_container)
        header_layout.addStretch(1)
        
        self.btn_toggle_sidebar_left = QPushButton("◂")
        self.btn_toggle_sidebar_left.setObjectName("IconButton")
        self.btn_toggle_sidebar_left.setFixedSize(28, 28)
        self.btn_toggle_sidebar_left.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.btn_toggle_sidebar_left)
        
        return header
    
    def _build_content(self):
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 4, 24, 20)
        content_layout.setSpacing(12)
        
        content_layout.addWidget(QLabel("当前项目"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumHeight(42)
        content_layout.addWidget(self.project_combo)
        
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        self.btn_new_project = QPushButton("新建")
        self.btn_delete_project = QPushButton("删除")
        self.btn_delete_project.setObjectName("DangerButton")
        self.btn_new_project.setMinimumHeight(36)
        self.btn_delete_project.setMinimumHeight(36)
        row1.addWidget(self.btn_new_project)
        row1.addWidget(self.btn_delete_project)
        content_layout.addLayout(row1)
        
        content_layout.addSpacing(12)
        content_layout.addWidget(QLabel("项目文风"))
        self.combo_project_style = QComboBox()
        self.combo_project_style.addItems(["正常模式", "番茄模式"])
        self.combo_project_style.setMinimumHeight(38)
        content_layout.addWidget(self.combo_project_style)
        
        content_layout.addStretch(1)
        
        content_layout.addWidget(self._build_settings_group())
        
        footer = QLabel("Powered by CrewAI")
        footer.setObjectName("FooterText")
        footer.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(footer)
        
        return content
    
    def _build_settings_group(self):
        box = QGroupBox("系统设置")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(16, 24, 16, 16)
        
        self.btn_api_settings = QPushButton("🔑 API 配置")
        self.btn_api_settings.setMinimumHeight(38)
        box_layout.addWidget(self.btn_api_settings)
        
        self.btn_license_settings = QPushButton("🛡️ 系统授权")
        self.btn_license_settings.setMinimumHeight(38)
        box_layout.addWidget(self.btn_license_settings)
        
        self.btn_model_params = QPushButton("⚙️ 参数设置")
        self.btn_model_params.setMinimumHeight(38)
        box_layout.addWidget(self.btn_model_params)
        
        return box
    
    def set_window_reference(self, window):
        self._window = window
