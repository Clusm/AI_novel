"""
侧边栏视图组件 - 优化版
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import DraggableHeader


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
        header.setObjectName("SidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        header_layout.setSpacing(12)
        
        # Logo使用渐变色背景
        logo_container = QWidget()
        logo_container.setObjectName("LogoContainer")
        logo_container.setFixedSize(32, 32)
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        logo = QLabel("AI")
        logo.setObjectName("LogoText")
        logo.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo)
        
        header_layout.addWidget(logo_container)
        
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title = QLabel("AI_Novel_Writer")
        title.setObjectName("BrandTitle")
        title_layout.addWidget(title)
        
        self.version_label = QLabel("v3.0")
        self.version_label.setObjectName("VersionText")
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
        content.setObjectName("SidebarContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 20)
        content_layout.setSpacing(0)
        
        # 当前项目区域
        content_layout.addWidget(self._create_section_label("当前项目"))
        
        self.project_combo = QComboBox()
        self.project_combo.setObjectName("ProjectSelector")
        self.project_combo.setMinimumHeight(42)
        content_layout.addWidget(self.project_combo)
        
        # 按钮组 - 新建为主按钮，删除为图标按钮
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.btn_new_project = QPushButton("➕ 新建")
        self.btn_new_project.setObjectName("PrimaryButtonSmall")
        self.btn_new_project.setMinimumHeight(36)
        
        self.btn_delete_project = QPushButton("🗑️")
        self.btn_delete_project.setObjectName("DangerIconButton")
        self.btn_delete_project.setFixedSize(36, 36)
        self.btn_delete_project.setToolTip("删除项目")
        
        row1.addWidget(self.btn_new_project, 1)
        row1.addWidget(self.btn_delete_project)
        content_layout.addLayout(row1)
        
        content_layout.addSpacing(20)
        
        # 项目文风区域
        content_layout.addWidget(self._create_section_label("项目文风"))
        
        self.combo_project_style = QComboBox()
        self.combo_project_style.setObjectName("StyleSelector")
        self.combo_project_style.addItems(["正常模式", "番茄模式"])
        self.combo_project_style.setMinimumHeight(40)
        content_layout.addWidget(self.combo_project_style)
        
        content_layout.addStretch(1)
        
        # 系统设置区域 - 使用分隔线替代GroupBox
        content_layout.addWidget(self._build_settings_section())
        
        # 底部品牌
        footer = QLabel("Powered by CrewAI")
        footer.setObjectName("FooterText")
        footer.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(footer)
        
        return content
    
    def _create_section_label(self, text):
        """创建分组标签"""
        label = QLabel(text)
        label.setObjectName("SectionLabel")
        return label
    
    def _build_settings_section(self):
        """构建设置区域 - 使用分隔线样式"""
        container = QWidget()
        container.setObjectName("SettingsContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 分隔线标题
        divider = QWidget()
        divider.setObjectName("Divider")
        divider_layout = QHBoxLayout(divider)
        divider_layout.setContentsMargins(0, 0, 0, 12)
        divider_layout.setSpacing(8)
        
        line_left = QWidget()
        line_left.setObjectName("DividerLine")
        line_left.setFixedHeight(1)
        
        divider_text = QLabel("系统设置")
        divider_text.setObjectName("DividerText")
        
        line_right = QWidget()
        line_right.setObjectName("DividerLine")
        line_right.setFixedHeight(1)
        
        divider_layout.addWidget(line_left, 1)
        divider_layout.addWidget(divider_text)
        divider_layout.addWidget(line_right, 1)
        
        layout.addWidget(divider)
        
        # 设置项列表
        self.btn_api_settings = QPushButton("🔑 API 配置")
        self.btn_api_settings.setObjectName("SettingItem")
        self.btn_api_settings.setMinimumHeight(38)
        layout.addWidget(self.btn_api_settings)
        
        self.btn_license_settings = QPushButton("🛡️ 系统授权")
        self.btn_license_settings.setObjectName("SettingItem")
        self.btn_license_settings.setMinimumHeight(38)
        layout.addWidget(self.btn_license_settings)
        
        self.btn_model_params = QPushButton("⚙️ 参数设置")
        self.btn_model_params.setObjectName("SettingItem")
        self.btn_model_params.setMinimumHeight(38)
        layout.addWidget(self.btn_model_params)
        
        return container
    
    def set_window_reference(self, window):
        self._window = window
