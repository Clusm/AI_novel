"""
创作中心 Tab 视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
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

        self.outline_stack = QStackedWidget()

        self.outline_edit = QPlainTextEdit()
        self.outline_edit.setObjectName("MarkdownEditor")
        self.outline_edit.setPlaceholderText("# 故事标题\n\n## 第一章：起航\n在这里写下你的故事大纲...")

        self.outline_preview = QTextEdit()
        self.outline_preview.setObjectName("ReaderContent")
        self.outline_preview.setReadOnly(True)

        self.outline_stack.addWidget(self.outline_edit)
        self.outline_stack.addWidget(self.outline_preview)

        mode_tabs = QHBoxLayout()
        mode_tabs.setSpacing(4)

        self.btn_write_mode = QPushButton("编辑")
        self.btn_write_mode.setCheckable(True)
        self.btn_write_mode.setChecked(True)
        self.btn_write_mode.setObjectName("SegmentedButton")
        self.btn_write_mode.setCursor(Qt.PointingHandCursor)
        self.btn_write_mode.setFixedSize(60, 28)

        self.btn_preview_mode = QPushButton("预览")
        self.btn_preview_mode.setCheckable(True)
        self.btn_preview_mode.setObjectName("SegmentedButton")
        self.btn_preview_mode.setCursor(Qt.PointingHandCursor)
        self.btn_preview_mode.setFixedSize(60, 28)

        # 使用 QButtonGroup 实现互斥
        self.outline_mode_group = QButtonGroup(self)
        self.outline_mode_group.setExclusive(True)
        self.outline_mode_group.addButton(self.btn_write_mode, 0)
        self.outline_mode_group.addButton(self.btn_preview_mode, 1)

        mode_tabs.addWidget(self.btn_write_mode)
        mode_tabs.addWidget(self.btn_preview_mode)
        mode_tabs.addStretch(1)

        left_layout.addLayout(mode_tabs)
        left_layout.addWidget(self.outline_stack, 1)

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
        mode_layout.setSpacing(4)
        
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
        
        radios.addWidget(self.radio_single)
        radios.addWidget(self.radio_batch)
        radios.addStretch(1)
        mode_layout.addLayout(radios)
        
        return mode_group
    
    def _build_settings_grid(self):
        grid_widget = QWidget()
        self.settings_grid = QGridLayout(grid_widget)
        self.settings_grid.setContentsMargins(0, 0, 0, 0)
        self.settings_grid.setHorizontalSpacing(16)
        self.settings_grid.setVerticalSpacing(6)
        self.settings_grid.setColumnStretch(0, 1)
        self.settings_grid.setColumnStretch(1, 1)
        
        self.lbl_start = QLabel("起始序号")
        self.lbl_start.setObjectName("MutedText")
        self.spin_start = QSpinBox()
        self.spin_start.setMinimum(1)
        self.spin_start.setMaximum(9999)
        self.spin_start.setMinimumHeight(52)
        self.spin_start.setAlignment(Qt.AlignCenter)
        
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
        
        return grid_widget
    
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
        
        return action_area
