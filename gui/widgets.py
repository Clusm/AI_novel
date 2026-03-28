"""
GUI 基础组件模块
包含：流重定向器、自定义标题栏、可拖拽头部、欢迎页组件、无边框窗口混入类
"""

import re
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from gui.styles import Colors, Typography, Radius, Sizes


class StreamRedirector(QObject):
    """
    流重定向器 - 将 stdout/stderr 输出重定向到 Qt 信号
    用于实时捕获控制台输出并显示在 UI 中
    """
    text_written = Signal(str)

    def __init__(self, original_stream=None):
        super().__init__()
        self.original_stream = original_stream

    def write(self, text):
        """写入文本，同时转发到原始流和发射 Qt 信号"""
        if self.original_stream and hasattr(self.original_stream, 'write'):
            try:
                self.original_stream.write(text)
                self.original_stream.flush()
            except Exception:
                pass
        self.text_written.emit(str(text))

    def flush(self):
        """刷新缓冲区"""
        if self.original_stream and hasattr(self.original_stream, 'flush'):
            try:
                self.original_stream.flush()
            except Exception:
                pass


class CustomTitleBar(QWidget):
    """
    自定义标题栏 - 支持最小化、最大化、关闭按钮
    实现无边框窗口的拖拽移动和双击最大化功能
    """
    def __init__(self, window, title="", min_btn=False, max_btn=False):
        super().__init__(window)
        self.window = window
        self.setFixedHeight(Sizes.TITLE_BAR_HEIGHT)
        self.setObjectName("TitleBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("TitleBarLabel")
        if title:
            layout.addWidget(self.title_label)
        layout.addStretch(1)

        if min_btn:
            self.btn_min = QPushButton("─")
            self.btn_min.setObjectName("TitleBarButton")
            self.btn_min.setFixedSize(28, 24)
            self.btn_min.clicked.connect(self.window.showMinimized)
            layout.addWidget(self.btn_min)

        if max_btn:
            self.btn_max = QPushButton("□")
            self.btn_max.setObjectName("TitleBarButton")
            self.btn_max.setFixedSize(28, 24)
            self.btn_max.clicked.connect(self.toggle_max)
            layout.addWidget(self.btn_max)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("TitleBarCloseButton")
        self.btn_close.setFixedSize(28, 24)
        self.btn_close.clicked.connect(self.window.close)
        layout.addWidget(self.btn_close)

    def toggle_max(self):
        """切换窗口最大化/正常状态"""
        if self.window.isMaximized():
            self.window.showNormal()
            self.btn_max.setText("□")
        else:
            self.window.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        """鼠标按下 - 记录拖拽起始位置"""
        if event.button() == Qt.LeftButton:
            self.window._drag_pos = event.globalPosition().toPoint() - self.window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动 - 执行窗口拖拽"""
        if event.buttons() == Qt.LeftButton and hasattr(self.window, '_drag_pos'):
            self.window.move(event.globalPosition().toPoint() - self.window._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        """双击 - 切换最大化状态"""
        if event.button() == Qt.LeftButton:
            self.toggle_max()
            event.accept()


class DraggableHeader(QWidget):
    """
    可拖拽头部组件 - 用于侧边栏等区域的拖拽移动
    """
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
    """
    欢迎页组件 - 显示应用启动时的引导界面
    包含：Logo、标题、副标题、三步骤引导卡片、开始按钮
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WelcomeWidget")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(32, 24, 32, 24)

        layout.addStretch(1)

        logo = QLabel("📖")
        logo.setStyleSheet(f"""
            font-size: 56px;
            background: transparent;
        """)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("AI 驱动的专业创作平台")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {Colors.TEXT_PRIMARY};
            margin-top: 12px;
            background: transparent;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("多Agent协作系统，让灵感即刻成书")
        subtitle.setStyleSheet(f"""
            font-size: {Typography.BODY['size']};
            color: {Colors.TEXT_TERTIARY};
            margin-bottom: 16px;
            background: transparent;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        steps_container = QWidget()
        steps_container.setStyleSheet("background: transparent;")
        steps_layout = QHBoxLayout(steps_container)
        steps_layout.setSpacing(16)
        steps_layout.setContentsMargins(0, 0, 0, 0)

        steps_data = [
            ("01", "新建项目", "创建你的小说项目"),
            ("02", "粘贴大纲", "输入故事大纲内容"),
            ("03", "一键生成", "AI自动创作章节")
        ]

        for step_num, step_title, step_desc in steps_data:
            card = QFrame()
            card.setObjectName("WelcomeStepCard")
            card.setFixedSize(Sizes.CARD_WIDTH_MD, 130)
            card.setStyleSheet(f"""
                QFrame#WelcomeStepCard {{
                    background-color: {Colors.SURFACE};
                    border: 1px solid {Colors.BORDER};
                    border-radius: {Radius.LG};
                }}
                QFrame#WelcomeStepCard:hover {{
                    border-color: {Colors.PRIMARY_300};
                    background-color: {Colors.PRIMARY_50};
                }}
            """)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(16)
            shadow.setYOffset(3)
            shadow.setColor(QColor(15, 23, 42, 15))
            card.setGraphicsEffect(shadow)

            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            card_layout.setSpacing(6)
            card_layout.setContentsMargins(12, 16, 12, 16)

            lbl_num = QLabel(step_num)
            lbl_num.setStyleSheet(f"""
                font-size: 28px;
                font-weight: {Typography.WEIGHT_EXTRABOLD};
                color: {Colors.PRIMARY_500};
                border: none;
                background: transparent;
            """)
            lbl_num.setAlignment(Qt.AlignCenter)

            lbl_title = QLabel(step_title)
            lbl_title.setStyleSheet(f"""
                font-size: {Typography.BODY['size']};
                font-weight: {Typography.WEIGHT_BOLD};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                background: transparent;
            """)
            lbl_title.setAlignment(Qt.AlignCenter)

            lbl_desc = QLabel(step_desc)
            lbl_desc.setStyleSheet(f"""
                font-size: {Typography.CAPTION["size"]};
                color: {Colors.TEXT_TERTIARY};
                border: none;
                background: transparent;
            """)
            lbl_desc.setAlignment(Qt.AlignCenter)

            card_layout.addWidget(lbl_num)
            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_desc)

            steps_layout.addWidget(card)

        layout.addWidget(steps_container)
        layout.setAlignment(steps_container, Qt.AlignCenter)

        layout.addSpacing(24)

        self.btn_start = QPushButton("开始创作")
        self.btn_start.setObjectName("PrimaryButton")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.setFixedSize(140, Sizes.BUTTON_HEIGHT_LG + 4)
        self.btn_start.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.GRADIENT_PRIMARY};
                color: {Colors.WHITE};
                border: none;
                border-radius: {Radius.MD};
                font-size: {Typography.BODY['size']};
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
            QPushButton:hover {{
                background: {Colors.PRIMARY_600};
            }}
            QPushButton:pressed {{
                background: {Colors.PRIMARY_700};
            }}
        """)

        layout.addWidget(self.btn_start, 0, Qt.AlignCenter)

        layout.addStretch(2)


class FramelessWindowMixin:
    """
    无边框窗口混入类 - 为窗口提供无边框、透明背景、自定义标题栏功能
    使用方式：class MyWindow(QMainWindow, FramelessWindowMixin)
    """
    def init_frameless(self, title="", min_btn=False, max_btn=False, translucent=True):
        """初始化无边框窗口：设置窗口标志、透明背景、创建标题栏"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, bool(translucent))
        self.title_bar = CustomTitleBar(self, title, min_btn, max_btn)
        return self.title_bar


def detect_outline_chapters(outline_text):
    """
    检测大纲中的章节数量
    返回：(检测到的章节数, 估算的章节数)
    通过正则匹配"第N章"格式的标题
    """
    if not outline_text:
        return 0, 0

    start_index = 0
    match = re.search(r'#+\s*分卷细纲|#+\s*章节大纲', outline_text)
    if match:
        start_index = match.end()

    chapter_matches = re.findall(r'(?:^|\n)#*\s*第\s*\d+\s*章', outline_text[start_index:])
    detected = len(chapter_matches)

    return detected, detected


def apply_drop_shadow(widget, blur_radius=24, y_offset=4, alpha=20):
    """
    为控件添加阴影效果
    参数：控件、模糊半径、Y偏移、透明度
    """
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur_radius)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(15, 23, 42, alpha))
    widget.setGraphicsEffect(effect)
