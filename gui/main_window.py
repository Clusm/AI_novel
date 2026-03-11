import os
import re
from datetime import datetime
from html import escape

from PySide6.QtCore import QEvent, Qt, QThread
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QGraphicsDropShadowEffect,
    QRadioButton,
    QScrollArea,
    QSizeGrip,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.styles import APP_STYLESHEET
from gui.workers import ChapterGenerationWorker
from src.api import load_api_keys, save_api_keys, test_all_apis
from src.logger import add_run_log, clear_run_logs
from src.project import (
    create_new_project,
    delete_project,
    get_all_projects,
    list_generated_chapters,
    load_chapter,
    load_outline,
    save_outline,
)


class CustomTitleBar(QWidget):
    def __init__(self, window, title="", min_btn=False, max_btn=False):
        super().__init__(window)
        self.window = window  # Store reference to main window
        self.setFixedHeight(40)
        self.setObjectName("TitleBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        
        self.title_label = QLabel(title)
        self.title_label.setObjectName("TitleBarLabel")
        if title:
            layout.addWidget(self.title_label)
        layout.addStretch(1)
        
        if min_btn:
            self.btn_min = QPushButton("─")
            self.btn_min.setObjectName("TitleBarButton")
            self.btn_min.clicked.connect(self.window.showMinimized)
            layout.addWidget(self.btn_min)
            
        if max_btn:
            self.btn_max = QPushButton("☐")
            self.btn_max.setObjectName("TitleBarButton")
            self.btn_max.clicked.connect(self.toggle_max)
            layout.addWidget(self.btn_max)
            
        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("TitleBarCloseButton")
        self.btn_close.clicked.connect(self.window.close)
        layout.addWidget(self.btn_close)
        
    def toggle_max(self):
        if self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window._drag_pos = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self.window, '_drag_pos'):
            self.window.move(event.globalPosition().toPoint() - self.window._drag_pos)
            event.accept()


class DraggableHeader(QWidget):
    """A helper widget that allows dragging the window"""
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window._drag_pos = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self.window, '_drag_pos'):
            self.window.move(event.globalPosition().toPoint() - self.window._drag_pos)
            event.accept()


class WelcomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Spacer
        layout.addStretch(1)
        
        # Logo placeholder
        logo = QLabel("🤖")
        logo.setStyleSheet("font-size: 64px; background: transparent;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # Title
        title = QLabel("欢迎使用多Agent编写系统")
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: #1e293b; margin-top: 20px; background: transparent;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("专业的AI辅助创作平台，让灵感即刻成书。")
        subtitle.setStyleSheet("font-size: 16px; color: #64748b; margin-bottom: 40px; background: transparent;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Steps
        steps_container = QWidget()
        steps_layout = QHBoxLayout(steps_container)
        steps_layout.setSpacing(30)
        steps_layout.setContentsMargins(0, 0, 0, 0)
        
        steps_data = [
            ("步骤 1", "新建项目"),
            ("步骤 2", "粘贴大纲"),
            ("步骤 3", "一键生成")
        ]
        
        for step_title, step_desc in steps_data:
            card = QFrame()
            card.setFixedSize(200, 160)
            card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 16px;
                }
            """)
            
            # Apply shadow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 15))
            card.setGraphicsEffect(shadow)
            
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            card_layout.setSpacing(10)
            
            lbl_title = QLabel(step_title)
            lbl_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #0f172a; border: none; background: transparent;")
            lbl_title.setAlignment(Qt.AlignCenter)
            
            lbl_desc = QLabel(step_desc)
            lbl_desc.setStyleSheet("font-size: 16px; color: #64748b; border: none; background: transparent;")
            lbl_desc.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_desc)
            
            steps_layout.addWidget(card)
            
        layout.addWidget(steps_container)
        layout.setAlignment(steps_container, Qt.AlignCenter)
        
        # Spacer
        layout.addSpacing(60)
        
        # Button
        self.btn_start = QPushButton("✨ 立即开始创作")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setFixedSize(240, 56)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        
        layout.addWidget(self.btn_start, 0, Qt.AlignCenter)
        
        layout.addStretch(2)



class FramelessWindowMixin:
    def init_frameless(self, title="", min_btn=False, max_btn=False, translucent=True):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, bool(translucent))
        self.title_bar = CustomTitleBar(self, title, min_btn, max_btn)
        return self.title_bar


def detect_outline_chapters(outline_text):
    text = outline_text or ""
    patterns = [r"第\s*\d+\s*章", r"Chapter\s*\d+", r"章节\s*\d+", r"\d+\s*\.", r"\d+\s*-", r"\[\d+\]"]
    detected = 0
    for pattern in patterns:
        detected += len(re.findall(pattern, text))
    if detected == 0:
        outline_length = len(text)
        if outline_length < 100:
            estimated = 3
        elif outline_length < 500:
            estimated = 5
        elif outline_length < 1000:
            estimated = 8
        else:
            estimated = 12
        return detected, estimated
    return detected, detected


def apply_drop_shadow(widget, blur_radius=24, y_offset=4, alpha=20):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(15, 23, 42, alpha))
    widget.setGraphicsEffect(effect)


class NewProjectDialog(QDialog, FramelessWindowMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(460)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10) # Margin for shadow
        layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setObjectName("DialogContainer")
        layout.addWidget(self.container)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        container_layout.addWidget(self.title_bar)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(20)
        
        title = QLabel("创建你的下一部杰作")
        title.setObjectName("PageTitle")
        content_layout.addWidget(title)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("项目名称，例如：诸天之无上道途")
        self.name_edit.setMinimumHeight(44)
        content_layout.addWidget(self.name_edit)
        
        btn_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("取消")
        self.ok_btn = QPushButton("立即创建")
        self.ok_btn.setObjectName("PrimaryButton")
        self.cancel_btn.setMinimumHeight(40)
        self.ok_btn.setMinimumHeight(40)
        
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        content_layout.addLayout(btn_layout)
        
        container_layout.addWidget(content)
        apply_drop_shadow(self.container, blur_radius=40, y_offset=12, alpha=30)

    def get_name(self):
        return self.name_edit.text().strip()


class ApiSettingsDialog(QDialog, FramelessWindowMixin):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(600)
        
        keys = load_api_keys()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setObjectName("DialogContainer")
        layout.addWidget(self.container)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        container_layout.addWidget(self.title_bar)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        header = QLabel("API & 模型设置")
        header.setObjectName("PageTitle")
        content_layout.addWidget(header)
        
        form = QFormLayout()
        form.setVerticalSpacing(16)
        
        self.deepseek = QLineEdit(keys.get("DEEPSEEK_API_KEY", ""))
        self.qwen = QLineEdit(keys.get("DASHSCOPE_API_KEY", ""))
        self.kimi = QLineEdit(keys.get("MOONSHOT_API_KEY", ""))
        self.auth_code = QLineEdit(keys.get("AUTH_CODE", ""))
        
        for field in [self.deepseek, self.qwen, self.kimi, self.auth_code]:
            field.setEchoMode(QLineEdit.Password)
            field.setMinimumHeight(40)
            
        self.route_profile = QComboBox()
        self.route_profile.addItems(["speed", "balanced", "quality"])
        self.route_profile.setMinimumHeight(40)
        route_val = keys.get("ROUTE_PROFILE", "speed")
        if route_val in ["speed", "balanced", "quality"]:
            self.route_profile.setCurrentText(route_val)
            
        self.writer_model = QComboBox()
        self.writer_model.addItems(["auto", "qwen", "kimi"])
        self.writer_model.setMinimumHeight(40)
        writer_val = keys.get("WRITER_MODEL", "auto")
        if writer_val in ["auto", "qwen", "kimi"]:
            self.writer_model.setCurrentText(writer_val)
            
        form.addRow("DeepSeek Key", self.deepseek)
        form.addRow("通义千问 Key", self.qwen)
        form.addRow("Kimi Key", self.kimi)
        form.addRow("系统授权码", self.auth_code)
        form.addRow("路由策略", self.route_profile)
        form.addRow("主写模型", self.writer_model)
        content_layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存配置并验证")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setMinimumHeight(42)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(42)
        
        self.result_label = QLabel("")
        self.result_label.setObjectName("Banner")
        self.result_label.setProperty("tone", "info")
        self.result_label.setWordWrap(True)
        self.result_label.setVisible(False)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        content_layout.addWidget(self.result_label)
        content_layout.addLayout(btn_layout)
        
        container_layout.addWidget(content)
        
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.save_and_test)
        
        apply_drop_shadow(self.container, blur_radius=40, y_offset=12, alpha=30)

    def save_and_test(self):
        try:
            save_api_keys(
                self.deepseek.text().strip(),
                self.qwen.text().strip(),
                self.kimi.text().strip(),
                self.auth_code.text().strip(),
                self.route_profile.currentText(),
                self.writer_model.currentText(),
            )
            providers = ["deepseek", "qwen"]
            has_kimi = bool(self.kimi.text().strip())
            route_profile = self.route_profile.currentText()
            writer_model = self.writer_model.currentText()
            
            kimi_required = has_kimi and (
                route_profile in ("balanced", "quality")
                or writer_model == "kimi"
                or (writer_model == "auto" and route_profile == "quality")
            )
            if kimi_required:
                providers.append("kimi")
                
            self.result_label.setText("正在验证连接...")
            self.result_label.setVisible(True)
            self.repaint()
            
            results = test_all_apis(providers)
            all_ok = all(val[0] for val in results.values())
            
            lines = []
            for provider, (ok, msg) in results.items():
                status_icon = "✅" if ok else "❌"
                lines.append(f"{status_icon} {provider}: {msg if not ok else '连接成功'}")
                
            self.result_label.setText("\n".join(lines))
            self.result_label.setProperty("tone", "success" if all_ok else "danger")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)
            
            if all_ok:
                # Delay closing slightly so user can see success
                QThread.msleep(500)
                self.accept()
                
        except Exception as exc:
            self.result_label.setText(str(exc))
            self.result_label.setVisible(True)
            self.result_label.setProperty("tone", "danger")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)


class MainWindow(QMainWindow, FramelessWindowMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多Agent写作系统 Pro")
        self.init_frameless("", min_btn=True, max_btn=True, translucent=True)
        self.resize(1280, 800)
        self.setMinimumSize(1120, 720)
        self._center_window()
        self.setStyleSheet(APP_STYLESHEET)
        self._resize_margin = 8
        self._resize_edges = None
        self._resize_start_pos = None
        self._resize_start_geometry = None
        self._is_resizing = False
        
        self.selected_project = None
        self.run_logs = []
        self.is_generating = False
        self.current_chapter_idx = 0
        self.filtered_chapters = []
        self.worker_thread = None
        self.worker = None
        self._outline_syncing = False
        
        self._build_ui()
        self.refresh_projects()

    def _center_window(self):
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def _build_ui(self):
        root = QFrame()
        root.setObjectName("CentralWidget")
        root.setMouseTracking(True)
        root.installEventFilter(self)
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(6, 6, 6, 6)
        root_layout.setSpacing(0)
        
        # Build Sidebar and Main Panel
        self.sidebar = self._build_sidebar()
        self.main_panel = self._build_main_panel()
        
        # Right Side Container (Title Bar + Main Panel)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.title_bar)
        right_layout.addWidget(self.main_panel)
        
        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setObjectName("MainSplitter")
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(right_container)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setSizes([260, 1200])
        self.splitter.setHandleWidth(1) # Thin separator
        
        root_layout.addWidget(self.splitter)
        self._corner_grips = [QSizeGrip(root) for _ in range(4)]

    def _edge_flags(self, global_pos):
        rect = self.frameGeometry()
        x = global_pos.x() - rect.left()
        y = global_pos.y() - rect.top()
        w = rect.width()
        h = rect.height()
        margin = self._resize_margin
        left = x <= margin
        right = x >= w - margin
        top = y <= margin
        bottom = y >= h - margin
        return left, right, top, bottom

    def _cursor_for_edges(self, edges):
        left, right, top, bottom = edges
        if (left and top) or (right and bottom):
            return Qt.SizeFDiagCursor
        if (right and top) or (left and bottom):
            return Qt.SizeBDiagCursor
        if left or right:
            return Qt.SizeHorCursor
        if top or bottom:
            return Qt.SizeVerCursor
        return Qt.ArrowCursor

    def _apply_resize(self, global_pos):
        if not self._is_resizing or not self._resize_edges:
            return
        left, right, top, bottom = self._resize_edges
        start = self._resize_start_geometry
        dx = global_pos.x() - self._resize_start_pos.x()
        dy = global_pos.y() - self._resize_start_pos.y()
        min_w = self.minimumWidth()
        min_h = self.minimumHeight()

        new_left = start.left()
        new_right = start.right()
        new_top = start.top()
        new_bottom = start.bottom()

        if left:
            new_left = min(start.left() + dx, start.right() - min_w + 1)
        if right:
            new_right = max(start.right() + dx, start.left() + min_w - 1)
        if top:
            new_top = min(start.top() + dy, start.bottom() - min_h + 1)
        if bottom:
            new_bottom = max(start.bottom() + dy, start.top() + min_h - 1)

        self.setGeometry(new_left, new_top, new_right - new_left + 1, new_bottom - new_top + 1)

    def eventFilter(self, watched, event):
        if watched is self.centralWidget():
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                global_pos = event.globalPosition().toPoint()
                edges = self._edge_flags(global_pos)
                if any(edges):
                    self._resize_edges = edges
                    self._resize_start_pos = global_pos
                    self._resize_start_geometry = self.frameGeometry()
                    self._is_resizing = True
                    return True
            if event.type() == QEvent.MouseMove:
                global_pos = event.globalPosition().toPoint()
                if self._is_resizing:
                    self._apply_resize(global_pos)
                    return True
                self.setCursor(self._cursor_for_edges(self._edge_flags(global_pos)))
            if event.type() == QEvent.MouseButtonRelease and self._is_resizing:
                self._is_resizing = False
                self._resize_edges = None
                self._resize_start_pos = None
                self._resize_start_geometry = None
                self.setCursor(Qt.ArrowCursor)
                return True
        return super().eventFilter(watched, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, "_corner_grips"):
            return
        grip_size = 14
        rect = self.rect()
        self._corner_grips[0].setGeometry(0, 0, grip_size, grip_size)
        self._corner_grips[1].setGeometry(rect.width() - grip_size, 0, grip_size, grip_size)
        self._corner_grips[2].setGeometry(0, rect.height() - grip_size, grip_size, grip_size)
        self._corner_grips[3].setGeometry(rect.width() - grip_size, rect.height() - grip_size, grip_size, grip_size)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self.btn_toggle_sidebar.setStyleSheet("background: #e2e8f0; color: #334155;")
        else:
            self.sidebar.show()
            self.splitter.setSizes([260, 1200])
            self.btn_toggle_sidebar.setStyleSheet("")

    def _build_sidebar(self):
        panel = QFrame()
        panel.setObjectName("Sidebar")
        panel.setMinimumWidth(232)
        panel.setMaximumWidth(420)
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header (Draggable Area)
        header = DraggableHeader(self)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 8)
        header_layout.setSpacing(4)
        
        # Branding
        title = QLabel("🤖 AI 写作助手")
        title.setObjectName("Title")
        header_layout.addWidget(title)
        
        self.version_label = QLabel("Pro v2.4")
        self.version_label.setObjectName("MutedText")
        header_layout.addWidget(self.version_label)
        
        layout.addWidget(header)
        
        # Content Area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 8, 24, 28)
        content_layout.setSpacing(16)
        
        # Project Selector
        content_layout.addWidget(QLabel("当前项目"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumHeight(42)
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        content_layout.addWidget(self.project_combo)
        
        # Project Actions
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
        
        self.btn_new_project.clicked.connect(self.create_project)
        self.btn_delete_project.clicked.connect(self.remove_project)
        
        content_layout.addStretch(1)
        
        # Settings at bottom
        box = QGroupBox("系统设置")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(16, 24, 16, 16)
        self.btn_api_settings = QPushButton("🔑 API 配置")
        self.btn_api_settings.setMinimumHeight(38)
        box_layout.addWidget(self.btn_api_settings)
        self.btn_api_settings.clicked.connect(self.open_api_settings)
        content_layout.addWidget(box)
        
        footer = QLabel("Powered by CrewAI")
        footer.setObjectName("FooterText")
        footer.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(footer)
        
        layout.addWidget(content)
        
        return panel

    def _build_main_panel(self):
        panel = QWidget()
        panel.setObjectName("MainPanel")
        
        # Stacked Widget
        self.main_stack = QStackedWidget()
        
        # 1. Welcome Screen
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.btn_start.clicked.connect(self.create_project)
        self.main_stack.addWidget(self.welcome_widget)
        
        # 2. Dashboard
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        layout.setContentsMargins(36, 26, 36, 32)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_toggle_sidebar = QPushButton("☰")
        self.btn_toggle_sidebar.setObjectName("IconButton")
        self.btn_toggle_sidebar.setFixedSize(32, 32)
        self.btn_toggle_sidebar.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        header_layout.addWidget(self.btn_toggle_sidebar)
        
        header_layout.addSpacing(16)
        
        self.project_title = QLabel("欢迎使用")
        self.project_title.setObjectName("PageTitle")
        header_layout.addWidget(self.project_title)
        header_layout.addStretch(1)
        layout.addLayout(header_layout)
        
        # Stats Grid
        self.stats_widget = QWidget()
        self.stats_layout = QGridLayout(self.stats_widget)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_layout.setHorizontalSpacing(20)
        self.stats_layout.setVerticalSpacing(20)
        
        self.stat_cards = []
        stat_labels = ["已生成章节", "总字数", "平均字数/章", "预计总章数"]
        bar_colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]
        
        for i, text in enumerate(stat_labels):
            card_wrapper = QFrame()
            card_wrapper.setObjectName("Card")
            
            # Remove default margins/padding from wrapper to let color bar sit flush
            wrapper_layout = QVBoxLayout(card_wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.setSpacing(0)
            
            # Color Bar
            color_bar = QFrame()
            color_bar.setObjectName("ColorBar")
            color_bar.setFixedHeight(6)
            color_bar.setStyleSheet(f"background: {bar_colors[i % len(bar_colors)]}; border-top-left-radius: 14px; border-top-right-radius: 14px;")
            wrapper_layout.addWidget(color_bar)
            
            # Content
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(4)

            value = QLabel("0")
            value.setAlignment(Qt.AlignCenter)
            value.setObjectName("StatValue")
            
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName("StatLabel")
            
            content_layout.addWidget(value)
            content_layout.addWidget(label)
            
            wrapper_layout.addLayout(content_layout)
            
            self.stat_cards.append(value)
            self.stats_layout.addWidget(card_wrapper, 0, i)
            
            # Drop shadow
            apply_drop_shadow(card_wrapper, blur_radius=20, y_offset=4, alpha=15)
            
        layout.addWidget(self.stats_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tab_create = self._build_tab_create()
        self.tab_reader = self._build_tab_reader()
        self.tab_monitor = self._build_tab_monitor()
        self.tab_export = self._build_tab_export()
        
        self.tabs.addTab(self.tab_create, "创作中心")
        self.tabs.addTab(self.tab_reader, "阅读管理")
        self.tabs.addTab(self.tab_monitor, "运行监控")
        self.tabs.addTab(self.tab_export, "导出发布")
        
        layout.addWidget(self.tabs, 1)
        
        self.main_stack.addWidget(dashboard)
        
        # Main Layout
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(self.main_stack)
        
        return panel

    def _build_tab_create(self):
        tab = QWidget()
        tab_layout = QHBoxLayout(tab)
        tab_layout.setContentsMargins(4, 14, 4, 4)
        tab_layout.setSpacing(20)
        
        # Left: Outline
        left = QFrame()
        left.setObjectName("Card")
        apply_drop_shadow(left, blur_radius=20, y_offset=4, alpha=15)
        
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.addWidget(QLabel("📝 故事大纲"))
        
        self.outline_edit = QTextEdit()
        self.outline_edit.setObjectName("MarkdownEditor")
        self.outline_edit.setPlaceholderText("# 故事标题\n\n## 第一章：起航\n在这里写下你的故事大纲...")
        self.outline_edit.textChanged.connect(self.on_outline_changed)
        left_layout.addWidget(self.outline_edit, 1)
        
        bottom = QHBoxLayout()
        self.btn_save_outline = QPushButton("保存大纲")
        self.btn_save_outline.setObjectName("PrimaryButton")
        self.btn_save_outline.clicked.connect(self.save_outline_clicked)
        
        self.chapter_detect_label = QLabel("")
        self.chapter_detect_label.setObjectName("MutedText")
        
        bottom.addWidget(self.btn_save_outline)
        bottom.addSpacing(10)
        bottom.addWidget(self.chapter_detect_label, 1)
        left_layout.addLayout(bottom)
        
        # Right: Generation Control
        right = QFrame()
        right.setObjectName("Card")
        right.setMaximumWidth(400)
        apply_drop_shadow(right, blur_radius=20, y_offset=4, alpha=15)
        
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(24) # Increased spacing
        
        right_layout.addWidget(QLabel("🚀 生成控制"))
        
        # 1. Mode Selection (Clean Horizontal)
        mode_group = QWidget()
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(4) # Reduced spacing
        
        mode_label = QLabel("创作模式")
        mode_label.setObjectName("MutedText")
        mode_layout.addWidget(mode_label)
        
        radios = QHBoxLayout()
        radios.setSpacing(20)
        self.radio_single = QRadioButton("单章精修")
        self.radio_batch = QRadioButton("批量速更")
        self.radio_single.setChecked(True)
        self.radio_single.setCursor(Qt.PointingHandCursor)
        self.radio_batch.setCursor(Qt.PointingHandCursor)
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_single)
        self.mode_group.addButton(self.radio_batch)
        self.radio_single.toggled.connect(self.sync_mode_ui)
        
        radios.addWidget(self.radio_single)
        radios.addWidget(self.radio_batch)
        radios.addStretch(1)
        mode_layout.addLayout(radios)
        
        right_layout.addWidget(mode_group)
        
        # 2. Settings Grid (Clean 2-Column)
        grid_widget = QWidget()
        self.settings_grid = QGridLayout(grid_widget)
        self.settings_grid.setContentsMargins(0, 0, 0, 0)
        self.settings_grid.setHorizontalSpacing(16)
        self.settings_grid.setVerticalSpacing(6)
        self.settings_grid.setColumnStretch(0, 1)
        self.settings_grid.setColumnStretch(1, 1)
        
        # Column 1: Start
        self.lbl_start = QLabel("起始序号")
        self.lbl_start.setObjectName("MutedText")
        self.spin_start = QSpinBox()
        self.spin_start.setMinimum(1)
        self.spin_start.setMaximum(9999)
        self.spin_start.setMinimumHeight(52)
        self.spin_start.setAlignment(Qt.AlignCenter)
        
        # Column 2: Count
        self.lbl_count = QLabel("生成章数")
        self.lbl_count.setObjectName("MutedText")
        self.spin_count = QSpinBox()
        self.spin_count.setMinimum(1)
        self.spin_count.setMaximum(10)
        self.spin_count.setMinimumHeight(52)
        self.spin_count.setAlignment(Qt.AlignCenter)
        
        self.settings_grid.addWidget(self.lbl_start, 0, 0, 1, 1)
        self.settings_grid.addWidget(self.lbl_count, 0, 1, 1, 1)
        self.settings_grid.addWidget(self.spin_start, 1, 0, 1, 1)
        self.settings_grid.addWidget(self.spin_count, 1, 1, 1, 1)
        
        right_layout.addWidget(grid_widget)
        
        # 3. Hint Banner (Separated)
        self.smart_hint = QLabel("")
        self.smart_hint.setObjectName("Banner")
        self.smart_hint.setProperty("tone", "info")
        self.smart_hint.setWordWrap(True)
        self.smart_hint.setStyleSheet("margin-top: 0px;") # Removed top margin
        right_layout.addWidget(self.smart_hint)
        
        right_layout.addStretch(1)
        
        # 4. Action Button (Bottom)
        action_area = QVBoxLayout()
        action_area.setSpacing(12)
        
        self.btn_generate = QPushButton("启动生成引擎")
        self.btn_generate.setObjectName("PrimaryButton")
        self.btn_generate.setMinimumHeight(50)
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        self.btn_generate.clicked.connect(self.start_generation)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        
        self.progress_label = QLabel("就绪")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setObjectName("MutedText")
        
        action_area.addWidget(self.btn_generate)
        action_area.addWidget(self.progress)
        action_area.addWidget(self.progress_label)
        
        right_layout.addLayout(action_area)
        
        tab_layout.addWidget(left, 3)
        tab_layout.addWidget(right, 2)
        
        # Initialize UI state
        self.progress.setVisible(False)
        self.sync_mode_ui()
        
        return tab

    def _build_tab_reader(self):
        tab = QWidget()
        tab_layout = QHBoxLayout(tab)
        tab_layout.setContentsMargins(4, 14, 4, 4)
        tab_layout.setSpacing(20)
        
        # Left: Chapter List
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
        self.chapter_search.textChanged.connect(self.refresh_chapter_filter)
        left_layout.addWidget(self.chapter_search)
        
        self.chapter_combo = QComboBox()
        self.chapter_combo.currentIndexChanged.connect(self.on_chapter_selected)
        left_layout.addWidget(self.chapter_combo)
        
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("上一章")
        self.btn_next = QPushButton("下一章")
        self.btn_prev.clicked.connect(lambda: self.move_chapter(-1))
        self.btn_next.clicked.connect(lambda: self.move_chapter(1))
        nav.addWidget(self.btn_prev)
        nav.addWidget(self.btn_next)
        left_layout.addLayout(nav)
        
        left_layout.addStretch(1)
        
        # Right: Reader
        right = QFrame()
        right.setObjectName("Card")
        apply_drop_shadow(right, blur_radius=20, y_offset=4, alpha=15)
        
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Reader Header
        header = QFrame()
        header.setStyleSheet("border-bottom: 1px solid #e2e8f0; background: #f8fafc; border-top-left-radius: 16px; border-top-right-radius: 16px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)
        
        self.chapter_title = QLabel("暂无章节")
        self.chapter_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0f172a;")
        
        self.chapter_words = QLabel("0 字")
        self.chapter_words.setStyleSheet("color: #64748b; font-weight: 500;")
        
        header_layout.addWidget(self.chapter_title, 1)
        header_layout.addWidget(self.chapter_words)
        right_layout.addWidget(header)
        
        # Content
        self.chapter_content = QTextEdit()
        self.chapter_content.setObjectName("ReaderContent")
        self.chapter_content.setReadOnly(True)
        right_layout.addWidget(self.chapter_content, 1)
        
        tab_layout.addWidget(left, 1)
        tab_layout.addWidget(right, 3)
        return tab

    def _build_tab_monitor(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(4, 14, 4, 4)
        layout.setSpacing(20)
        
        # Logs
        logs = QFrame()
        logs.setObjectName("Card")
        apply_drop_shadow(logs, blur_radius=20, y_offset=4, alpha=15)
        
        logs_layout = QVBoxLayout(logs)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QFrame()
        header.setStyleSheet("border-bottom: 1px solid #e2e8f0; background: #f8fafc; border-top-left-radius: 16px; border-top-right-radius: 16px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 12, 20, 12)
        h_layout.addWidget(QLabel("📺 Agent 实时思维流"))
        h_layout.addStretch(1)
        
        self.btn_refresh_logs = QPushButton("刷新")
        self.btn_refresh_logs.setFixedSize(60, 30)
        self.btn_refresh_logs.setStyleSheet("padding: 4px;")
        self.btn_refresh_logs.clicked.connect(self.refresh_log_view)
        
        self.btn_clear_logs = QPushButton("清空")
        self.btn_clear_logs.setFixedSize(60, 30)
        self.btn_clear_logs.setStyleSheet("padding: 4px;")
        self.btn_clear_logs.clicked.connect(self.clear_logs_clicked)
        
        h_layout.addWidget(self.btn_refresh_logs)
        h_layout.addWidget(self.btn_clear_logs)
        logs_layout.addWidget(header)
        
        self.logs_view = QTextEdit()
        self.logs_view.setObjectName("LogViewer")
        self.logs_view.setReadOnly(True)
        # Remove border from log viewer as card has it
        self.logs_view.setStyleSheet("border: none; border-bottom-left-radius: 16px; border-bottom-right-radius: 16px;")
        logs_layout.addWidget(self.logs_view, 1)
        
        layout.addWidget(logs)
        return tab

    def _build_tab_export(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
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
        
        self.btn_export_word.clicked.connect(self.export_word_clicked)
        self.btn_export_epub.clicked.connect(self.export_epub_clicked)
        self.btn_export_txt.clicked.connect(self.export_txt_clicked)
        self.btn_export_all.clicked.connect(self.export_all_clicked)
        
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
        return tab

    def refresh_projects(self):
        projects = get_all_projects()
        current = self.selected_project
        self.project_combo.blockSignals(True)
        self.project_combo.clear()
        self.project_combo.addItems(projects)
        self.project_combo.blockSignals(False)
        if projects:
            if current in projects:
                self.selected_project = current
            else:
                self.selected_project = projects[0]
            self.project_combo.setCurrentText(self.selected_project)
        else:
            self.selected_project = None
        self.reload_project_data()

    def on_project_changed(self):
        name = self.project_combo.currentText().strip()
        self.selected_project = name if name else None
        self.reload_project_data()

    def reload_project_data(self):
        enabled = bool(self.selected_project)
        
        if not enabled:
            self.main_stack.setCurrentIndex(0) # Show Welcome
            self.btn_delete_project.setEnabled(False)
            return
            
        self.main_stack.setCurrentIndex(1) # Show Dashboard
        self.tabs.setEnabled(True)
        self.btn_delete_project.setEnabled(True)
        
        outline = load_outline(self.selected_project)
        chapters = list_generated_chapters(self.selected_project)
        detected, estimated = detect_outline_chapters(outline)
        total_target = detected if detected > 0 else estimated
        total_words = 0
        for chapter in chapters:
            total_words += len(load_chapter(self.selected_project, chapter))
        avg_words = int(total_words / len(chapters)) if chapters else 0
        self.project_title.setText(self.selected_project)
        self.stat_cards[0].setText(str(len(chapters)))
        self.stat_cards[1].setText(f"{total_words:,}")
        self.stat_cards[2].setText(f"{avg_words:,}")
        self.stat_cards[3].setText(str(total_target))
        self.outline_edit.blockSignals(True)
        self._set_outline_markdown(outline)
        self.outline_edit.blockSignals(False)
        if detected > 0:
            self.chapter_detect_label.setText(f"✅ 已识别 {detected} 个章节标题")
        else:
            self.chapter_detect_label.setText("⚠️ 未检测到标准章节标题（建议使用第N章）")
        self.sync_mode_ui()
        self.refresh_chapter_filter()
        self.refresh_log_view()

    def on_outline_changed(self):
        if self._outline_syncing:
            return
        plain_text = self.outline_edit.toPlainText()
        if re.search(r"(^|\n)\s*(#{1,6}\s+|[-*]\s+|\d+\.\s+|>\s+)", plain_text):
            current_markdown = self.outline_edit.toMarkdown().strip()
            if plain_text.strip() == current_markdown:
                cursor_pos = self.outline_edit.textCursor().position()
                self._outline_syncing = True
                self.outline_edit.setMarkdown(plain_text)
                restored = self.outline_edit.textCursor()
                restored.setPosition(min(cursor_pos, len(self.outline_edit.toPlainText())))
                self.outline_edit.setTextCursor(restored)
                self._outline_syncing = False
        text = self.outline_edit.toMarkdown()
        detected, _ = detect_outline_chapters(text)
        if detected > 0:
            self.chapter_detect_label.setText(f"✅ 已识别 {detected} 个章节标题")
        else:
            self.chapter_detect_label.setText("⚠️ 未检测到标准章节标题（建议使用第N章）")

    def _set_outline_markdown(self, text):
        self._outline_syncing = True
        self.outline_edit.setMarkdown(text or "")
        self._outline_syncing = False

    def _get_outline_markdown(self):
        return self.outline_edit.toMarkdown().strip()

    def _refresh_banner_style(self, label, tone):
        label.setProperty("tone", tone)
        label.style().unpolish(label)
        label.style().polish(label)

    def _show_export_result(self, message, tone):
        self.export_result.setText(message)
        self.export_result.setVisible(True)
        self._refresh_banner_style(self.export_result, tone)

    def _get_log_tone(self, text):
        if "[ERROR]" in text or "❌" in text:
            return "danger"
        if "[WARNING]" in text or "⚠️" in text:
            return "warning"
        if "[SUCCESS]" in text or "✅" in text:
            return "success"
        return "info"

    def _get_log_icon(self, tone):
        if tone == "danger":
            return "⛔"
        if tone == "warning":
            return "⚠️"
        if tone == "success":
            return "✅"
        return "ℹ️"

    def _format_log_html(self, text):
        tone = self._get_log_tone(text)
        bg_map = {
            "info": "transparent",
            "success": "rgba(22, 163, 74, 0.1)",
            "warning": "rgba(217, 119, 6, 0.1)",
            "danger": "rgba(220, 38, 38, 0.1)",
        }
        color_map = {
            "info": "#94a3b8",
            "success": "#4ade80",
            "warning": "#fbbf24",
            "danger": "#f87171",
        }
        
        escaped = escape(text)
        time_str = datetime.now().strftime("%H:%M:%S")
        
        if " | " in escaped:
            left, right = escaped.split(" | ", 1)
            escaped = f"<strong style='color:#e2e8f0;'>{left}</strong><br><span style='color:#cbd5e1;'>{right}</span>"
        else:
            escaped = f"<span style='color:#e2e8f0;'>{escaped}</span>"
            
        return (
            f"<div style='padding:8px 12px;margin:4px 0;background:{bg_map[tone]};"
            f"border-left:3px solid {color_map[tone]};border-radius:4px;'>"
            f"<span style='color:#64748b;font-size:12px;margin-right:10px;'>[{time_str}]</span>"
            f"{self._get_log_icon(tone)} {escaped}</div>"
        )

    def save_outline_clicked(self):
        if not self.selected_project:
            return
        save_outline(self.selected_project, self._get_outline_markdown())
        QMessageBox.information(self, "保存成功", "大纲已保存")
        self.reload_project_data()

    def sync_mode_ui(self):
        if not self.selected_project:
            self.spin_start.setVisible(True)
            self.smart_hint.setText("⚠️ 请先在左侧选择或创建项目")
            self._refresh_banner_style(self.smart_hint, "warning")
            return
        chapters = list_generated_chapters(self.selected_project)
        max_chap = 0
        for name in chapters:
            match = re.search(r"(\d+)", name)
            if match:
                max_chap = max(max_chap, int(match.group(1)))
        
        # Don't auto-reset start if already set by user interaction, 
        # unless it's the first load or invalid
        if self.spin_start.value() <= max_chap:
            self.spin_start.setValue(max_chap + 1)
            
        # Connect spin count change to update hint
        try:
            self.spin_count.valueChanged.disconnect(self.update_hint)
            self.spin_start.valueChanged.disconnect(self.update_hint)
        except:
            pass
        self.spin_count.valueChanged.connect(self.update_hint)
        self.spin_start.valueChanged.connect(self.update_hint)
        
        self.update_hint()

    def update_hint(self):
        if self.radio_batch.isChecked():
            self.spin_start.setVisible(True)
            self.lbl_start.setVisible(True)
            self.settings_grid.addWidget(self.lbl_start, 0, 0, 1, 1)
            self.settings_grid.addWidget(self.lbl_count, 0, 1, 1, 1)
            self.settings_grid.addWidget(self.spin_start, 1, 0, 1, 1)
            self.settings_grid.addWidget(self.spin_count, 1, 1, 1, 1)
            self.spin_count.setMaximum(10)
            self.smart_hint.setText(f"📅 计划任务：从第 {self.spin_start.value()} 章开始，连续生成 {self.spin_count.value()} 章")
            self._refresh_banner_style(self.smart_hint, "info")
        else:
            self.spin_start.setVisible(False)
            self.lbl_start.setVisible(False)
            self.settings_grid.addWidget(self.lbl_count, 0, 0, 1, 2)
            self.settings_grid.addWidget(self.spin_count, 1, 0, 1, 2)
            self.spin_count.setMaximum(5)
            self.smart_hint.setText(f"✍️ 即将生成：第 {self.spin_start.value()} 章")
            self._refresh_banner_style(self.smart_hint, "info")

    def create_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.get_name()
            if not name:
                QMessageBox.warning(self, "提示", "请输入项目名称")
                return
            try:
                created = create_new_project(name)
                self.selected_project = created
                self.refresh_projects()
            except Exception as exc:
                QMessageBox.critical(self, "创建失败", str(exc))

    def remove_project(self):
        if not self.selected_project:
            return
        answer = QMessageBox.question(self, "确认删除", f"确定删除项目 {self.selected_project} 吗？")
        if answer != QMessageBox.Yes:
            return
        delete_project(self.selected_project)
        self.selected_project = None
        self.refresh_projects()

    def open_api_settings(self):
        dialog = ApiSettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            QMessageBox.information(self, "配置成功", "配置已保存且连接正常")

    def start_generation(self):
        if self.is_generating:
            return
        if not self.selected_project:
            QMessageBox.warning(self, "提示", "请先创建或选择项目")
            return
        outline = self._get_outline_markdown().strip()
        if len(outline) < 50:
            QMessageBox.warning(self, "提示", "请先完善大纲（至少 50 字）")
            return
        self.is_generating = True
        self.btn_generate.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress_label.setText("正在初始化生成引擎...")
        self.run_logs = []
        self.refresh_log_view()
        
        # Auto-switch to Monitor tab to show logs
        self.tabs.setCurrentWidget(self.tab_monitor)
        
        if self.radio_batch.isChecked():
            start = self.spin_start.value()
        else:
            chapters = list_generated_chapters(self.selected_project)
            max_chap = 0
            for name in chapters:
                match = re.search(r"(\d+)", name)
                if match:
                    max_chap = max(max_chap, int(match.group(1)))
            start = max_chap + 1
        count = self.spin_count.value()
        self.worker_thread = QThread(self)
        self.worker = ChapterGenerationWorker(self.selected_project, outline, start, count)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.log.connect(self.on_worker_log)
        self.worker.progress.connect(self.on_worker_progress)
        self.worker.chapter_done.connect(self.on_worker_chapter_done)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def on_worker_log(self, message, status):
        add_run_log(self.run_logs, "Agent流", message, status)
        self.refresh_log_view()

    def on_worker_progress(self, done, total, text):
        ratio = 0 if total <= 0 else int(done * 100 / total)
        self.progress.setValue(ratio)
        self.progress_label.setText(text)

    def on_worker_chapter_done(self, chapter_number):
        msg = f"第 {chapter_number} 章生成完成"
        add_run_log(self.run_logs, "系统", msg, "success")
        self.refresh_log_view()
        self.reload_project_data()

    def on_worker_finished(self, success, message):
        self.is_generating = False
        self.btn_generate.setEnabled(True)
        self.progress.setVisible(False)
        if success:
            self.progress.setValue(100)
            add_run_log(self.run_logs, "系统", message, "success")
            self.refresh_log_view()
        else:
            QMessageBox.warning(self, "任务结束", message)
        self.reload_project_data()
        self.worker = None
        self.worker_thread = None

    def refresh_chapter_filter(self):
        if not self.selected_project:
            self.filtered_chapters = []
            self.chapter_combo.clear()
            return
        all_chapters = list_generated_chapters(self.selected_project)
        keyword = self.chapter_search.text().strip()
        self.filtered_chapters = [c for c in all_chapters if keyword in c] if keyword else all_chapters
        self.chapter_combo.blockSignals(True)
        self.chapter_combo.clear()
        self.chapter_combo.addItems(self.filtered_chapters)
        self.chapter_combo.blockSignals(False)
        if not self.filtered_chapters:
            self.current_chapter_idx = 0
            self.chapter_title.setText("暂无章节")
            self.chapter_words.setText("0 字")
            self.chapter_content.setMarkdown("")
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            return
        self.current_chapter_idx = min(self.current_chapter_idx, len(self.filtered_chapters) - 1)
        self.chapter_combo.setCurrentIndex(self.current_chapter_idx)
        self.show_current_chapter()

    def on_chapter_selected(self):
        idx = self.chapter_combo.currentIndex()
        if idx < 0:
            return
        self.current_chapter_idx = idx
        self.show_current_chapter()

    def move_chapter(self, offset):
        if not self.filtered_chapters:
            return
        self.current_chapter_idx += offset
        self.current_chapter_idx = max(0, min(self.current_chapter_idx, len(self.filtered_chapters) - 1))
        self.chapter_combo.setCurrentIndex(self.current_chapter_idx)
        self.show_current_chapter()

    def show_current_chapter(self):
        if not self.filtered_chapters:
            return
        chapter_file = self.filtered_chapters[self.current_chapter_idx]
        content = load_chapter(self.selected_project, chapter_file)
        self.chapter_title.setText(chapter_file.replace(".md", ""))
        self.chapter_words.setText(f"{len(content)} 字")
        self.chapter_content.setMarkdown(content)
        self.btn_prev.setEnabled(self.current_chapter_idx > 0)
        self.btn_next.setEnabled(self.current_chapter_idx < len(self.filtered_chapters) - 1)

    def clear_logs_clicked(self):
        clear_run_logs(self.run_logs)
        self.refresh_log_view()

    def refresh_log_view(self):
        if not self.run_logs:
            self.logs_view.setHtml("<p style='color:#64748b; font-family:sans-serif;'>等待任务启动...</p>")
            return
        blocks = [self._format_log_html(log) for log in reversed(self.run_logs)]
        self.logs_view.setHtml("".join(blocks))
        self.logs_view.verticalScrollBar().setValue(self.logs_view.verticalScrollBar().maximum())

    def _export_guard(self):
        if not self.selected_project:
            QMessageBox.warning(self, "提示", "请先选择项目")
            return False
        return True

    def export_word_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_to_word
            path = export_to_word(self.selected_project)
            self._show_export_result(f"已导出: {os.path.basename(path)}", "success")
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")

    def export_epub_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_to_epub
            path = export_to_epub(self.selected_project)
            self._show_export_result(f"已导出: {os.path.basename(path)}", "success")
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")

    def export_txt_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_to_txt
            path = export_to_txt(self.selected_project)
            self._show_export_result(f"已导出: {os.path.basename(path)}", "success")
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")

    def export_all_clicked(self):
        if not self._export_guard():
            return
        try:
            from src.export import export_all_formats
            paths = export_all_formats(self.selected_project)
            self._show_export_result(f"全部导出成功: {os.path.dirname(paths['txt'])}", "success")
        except Exception as exc:
            self._show_export_result(f"导出失败: {exc}", "danger")
