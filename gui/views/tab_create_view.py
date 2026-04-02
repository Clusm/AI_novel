"""
创作中心 Tab 视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from gui.widgets import apply_drop_shadow
from gui.styles import Colors, Typography, Radius


class TabCreateView(QWidget):
    """
    创作中心标签页 - 包含大纲编辑和生成控制
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        tab_layout = QHBoxLayout(self)
        tab_layout.setContentsMargins(4, 14, 4, 4)
        tab_layout.setSpacing(20)

        tab_layout.addWidget(self._build_outline_panel(), 4)
        tab_layout.addWidget(self._build_control_panel(), 2)

        self.progress.setVisible(False)

    def _build_outline_panel(self):
        left = QFrame()
        left.setObjectName("Card")
        apply_drop_shadow(left, blur_radius=20, y_offset=4, alpha=15)

        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(20, 20, 20, 10)
        left_layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.addWidget(QLabel("📝 故事大纲"))

        self.chapter_detect_label = QLabel("")
        self.chapter_detect_label.setObjectName("MutedText")
        self.chapter_detect_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_row.addWidget(self.chapter_detect_label, 1)

        left_layout.addLayout(header_row)

        self.outline_preview = QTextEdit()
        self.outline_preview.setObjectName("ReaderContent")
        self.outline_preview.setReadOnly(True)
        left_layout.addWidget(self.outline_preview, 1)

        tools = QHBoxLayout()
        tools.setContentsMargins(0, 0, 0, 0)
        tools.addStretch(1)

        self.btn_save_outline = QPushButton("保存大纲")
        self.btn_save_outline.setObjectName("PrimaryButton")
        self.btn_save_outline.setFixedSize(100, 36)
        tools.addWidget(self.btn_save_outline)
        left_layout.addLayout(tools)

        return left
    
    def _build_control_panel(self):
        right = QFrame()
        right.setObjectName("Card")
        right.setMaximumWidth(400)
        apply_drop_shadow(right, blur_radius=20, y_offset=4, alpha=15)
        
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(24)
        
        right_layout.addWidget(QLabel("🚀 生成控制"))
        right_layout.addWidget(self._build_mode_selector())
        right_layout.addWidget(self._build_settings_grid())
        right_layout.addWidget(self._build_hint_banner())
        right_layout.addStretch(1)
        right_layout.addLayout(self._build_action_area())
        
        return right
    
    def _build_mode_selector(self):
        mode_group = QWidget()
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)

        mode_label = QLabel("生成模式")
        mode_label.setObjectName("MutedText")
        mode_layout.addWidget(mode_label)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["新建章节", "重写章节"])
        self.combo_mode.setMinimumHeight(40)
        self.combo_mode.setCursor(Qt.PointingHandCursor)
        mode_layout.addWidget(self.combo_mode)

        return mode_group
    
    def _build_settings_grid(self):
        self.settings_stack = QStackedWidget()

        # 新建章节页面
        new_widget = QWidget()
        new_grid = QGridLayout(new_widget)
        new_grid.setContentsMargins(0, 0, 0, 0)
        new_grid.setHorizontalSpacing(20)
        new_grid.setVerticalSpacing(8)
        new_grid.setColumnStretch(0, 1)
        new_grid.setColumnStretch(1, 1)

        self.lbl_start = QLabel("起始序号")
        self.lbl_start.setObjectName("MutedText")
        self.spin_start = QSpinBox()
        self.spin_start.setMinimum(1)
        self.spin_start.setMaximum(9999)
        self.spin_start.setMinimumHeight(48)
        self.spin_start.setAlignment(Qt.AlignCenter)

        self.lbl_count = QLabel("生成章数")
        self.lbl_count.setObjectName("MutedText")
        self.spin_count = QSpinBox()
        self.spin_count.setMinimum(1)
        self.spin_count.setMaximum(10)
        self.spin_count.setMinimumHeight(48)
        self.spin_count.setAlignment(Qt.AlignCenter)

        new_grid.addWidget(self.lbl_start, 0, 0, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        new_grid.addWidget(self.lbl_count, 0, 1, 1, 1, Qt.AlignLeft | Qt.AlignBottom)
        new_grid.addWidget(self.spin_start, 1, 0, 1, 1)
        new_grid.addWidget(self.spin_count, 1, 1, 1, 1)

        # 重写章节页面
        rewrite_widget = QWidget()
        rewrite_layout = QVBoxLayout(rewrite_widget)
        rewrite_layout.setContentsMargins(0, 0, 0, 0)
        rewrite_layout.setSpacing(8)

        lbl_chapter = QLabel("选择章节")
        lbl_chapter.setObjectName("MutedText")
        rewrite_layout.addWidget(lbl_chapter)

        self.combo_chapter = QComboBox()
        self.combo_chapter.setMinimumHeight(40)
        self.combo_chapter.setCursor(Qt.PointingHandCursor)
        rewrite_layout.addWidget(self.combo_chapter)

        lbl_suggestion = QLabel("重写建议")
        lbl_suggestion.setObjectName("MutedText")
        rewrite_layout.addWidget(lbl_suggestion)

        self.text_suggestion = QPlainTextEdit()
        self.text_suggestion.setPlaceholderText("输入重写建议，例如：增强情感描写、加快节奏...")
        self.text_suggestion.setMinimumHeight(100)
        self.text_suggestion.setMaximumHeight(150)
        rewrite_layout.addWidget(self.text_suggestion)

        self.settings_stack.addWidget(new_widget)
        self.settings_stack.addWidget(rewrite_widget)

        return self.settings_stack
    
    def _build_hint_banner(self):
        self.smart_hint = QLabel("")
        self.smart_hint.setObjectName("Banner")
        self.smart_hint.setProperty("tone", "info")
        self.smart_hint.setWordWrap(True)
        self.smart_hint.setStyleSheet("margin-top: 0px;")
        return self.smart_hint
    
    def _build_action_area(self):
        action_area = QVBoxLayout()
        action_area.setSpacing(12)

        self.btn_generate = QPushButton("启动生成引擎")
        self.btn_generate.setObjectName("PrimaryButton")
        self.btn_generate.setMinimumHeight(50)
        self.btn_generate.setCursor(Qt.PointingHandCursor)

        self.btn_stop = QPushButton("停止生成")
        self.btn_stop.setObjectName("DangerButton")
        self.btn_stop.setMinimumHeight(50)
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setVisible(False)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)

        self.progress_label = QLabel("就绪")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setObjectName("MutedText")

        action_area.addWidget(self.btn_generate)
        action_area.addWidget(self.btn_stop)
        action_area.addWidget(self.progress)
        action_area.addWidget(self.progress_label)

        return action_area
