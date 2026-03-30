"""
GUI 对话框模块
包含：新建项目对话框、API设置对话框、模型参数对话框、授权管理对话框、自定义消息框
"""

from PySide6.QtCore import Qt, QThread
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from gui.styles import Colors, Typography, Sizes, Radius
from gui.widgets import FramelessWindowMixin, apply_drop_shadow
from src.api import (
    MODEL_ROLE_LABELS,
    MODEL_ROLES,
    load_api_keys,
    save_api_keys,
    resolve_runtime_role_models,
    get_model_capability_limits,
)


class CustomMessageBox(QDialog, FramelessWindowMixin):
    """
    自定义消息框 - 替代原生 QMessageBox，与无边框设计风格统一
    支持 information、question、warning 三种类型
    """
    
    ICON_MAP = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "danger": "⛔",
        "question": "❓",
    }
    
    COLOR_MAP = {
        "info": Colors.PRIMARY_500,
        "success": Colors.SUCCESS_500,
        "warning": Colors.WARNING_500,
        "danger": Colors.ERROR_500,
        "question": Colors.PRIMARY_500,
    }
    
    def __init__(self, parent=None, title="", message="", msg_type="info", callback=None):
        super().__init__(parent)
        self._callback = callback
        self._result = None
        self._msg_type = msg_type
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(360)
        
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
        content_layout.setContentsMargins(24, 20, 24, 24)
        content_layout.setSpacing(16)
        
        icon_label = QLabel(self.ICON_MAP.get(msg_type, "ℹ️"))
        icon_label.setStyleSheet(f"font-size: 48px; background: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(icon_label)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                font-size: {Typography.H3['size']};
                font-weight: {Typography.WEIGHT_BOLD};
                color: {Colors.TEXT_PRIMARY};
                background: transparent;
            """)
            title_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(title_label)
        
        msg_label = QLabel(message)
        msg_label.setStyleSheet(f"""
            font-size: {Typography.BODY['size']};
            color: {Colors.TEXT_SECONDARY};
            background: transparent;
        """)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(msg_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        if msg_type == "question":
            self._yes_btn = QPushButton("确定")
            self._yes_btn.setObjectName("PrimaryButton")
            self._yes_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
            self._yes_btn.setMinimumWidth(80)
            self._yes_btn.clicked.connect(self._on_yes)
            
            self._no_btn = QPushButton("取消")
            self._no_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
            self._no_btn.setMinimumWidth(80)
            self._no_btn.clicked.connect(self._on_no)
            
            btn_layout.addStretch(1)
            btn_layout.addWidget(self._yes_btn)
            btn_layout.addWidget(self._no_btn)
            btn_layout.addStretch(1)
        else:
            self._ok_btn = QPushButton("确定")
            self._ok_btn.setObjectName("PrimaryButton")
            self._ok_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
            self._ok_btn.setMinimumWidth(100)
            self._ok_btn.clicked.connect(self.accept)
            
            btn_layout.addStretch(1)
            btn_layout.addWidget(self._ok_btn)
            btn_layout.addStretch(1)
        
        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content)
        
        apply_drop_shadow(self.container, blur_radius=32, y_offset=8, alpha=25)
    
    def _on_yes(self):
        self._result = True
        if self._callback:
            self._callback(True)
        self.accept()
    
    def _on_no(self):
        self._result = False
        if self._callback:
            self._callback(False)
        self.reject()

    def closeEvent(self, event):
        """处理窗口关闭事件"""
        if self._msg_type == "question":
            self._result = False  # 关闭视为取消
        event.accept()

    @staticmethod
    def information(parent, title, message):
        """显示信息提示框"""
        dlg = CustomMessageBox(parent, title, message, "info")
        dlg.exec()
        return True
    
    @staticmethod
    def success(parent, title, message):
        """显示成功提示框"""
        dlg = CustomMessageBox(parent, title, message, "success")
        dlg.exec()
        return True
    
    @staticmethod
    def warning(parent, title, message):
        """显示警告提示框"""
        dlg = CustomMessageBox(parent, title, message, "warning")
        dlg.exec()
        return True
    
    @staticmethod
    def critical(parent, title, message):
        """显示错误提示框"""
        dlg = CustomMessageBox(parent, title, message, "danger")
        dlg.exec()
        return True
    
    @staticmethod
    def question(parent, title, message, callback=None):
        """显示确认对话框，返回用户是否点击确定"""
        dlg = CustomMessageBox(parent, title, message, "question", callback)
        result = dlg.exec()
        if callback is None:
            return dlg._result if dlg._result is not None else (result == QDialog.Accepted)
        return dlg._result if dlg._result is not None else False


class NewProjectDialog(QDialog, FramelessWindowMixin):
    """
    新建项目对话框 - 用于创建新的小说项目
    功能：输入项目名称、选择文风模式（正常/番茄）
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(Sizes.DIALOG_WIDTH_SM)

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
        content_layout.setContentsMargins(20, 8, 20, 20)
        content_layout.setSpacing(8)

        title = QLabel("创建新项目")
        title.setObjectName("PageTitle")
        content_layout.addWidget(title)

        desc = QLabel("为你的小说项目命名，选择创作风格")
        desc.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-size: {Typography.CAPTION['size']};")
        content_layout.addWidget(desc)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：诸天之无上道途")
        self.name_edit.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
        self.name_edit.setClearButtonEnabled(False)
        content_layout.addWidget(self.name_edit)

        style_label = QLabel("文风偏好")
        style_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-weight: {Typography.WEIGHT_MEDIUM}; margin-top: 4px; font-size: {Typography.CAPTION['size']};")
        content_layout.addWidget(style_label)

        self.style_combo = QComboBox()
        self.style_combo.addItems(["正常模式", "番茄模式"])
        self.style_combo.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
        content_layout.addWidget(self.style_combo)

        content_layout.addSpacing(8)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.cancel_btn = QPushButton("取消")
        self.ok_btn = QPushButton("创建项目")
        self.ok_btn.setObjectName("PrimaryButton")
        self.cancel_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
        self.ok_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        content_layout.addLayout(btn_layout)

        container_layout.addWidget(content)
        apply_drop_shadow(self.container, blur_radius=32, y_offset=8, alpha=25)

    def get_name(self):
        """获取用户输入的项目名称"""
        return self.name_edit.text().strip()

    def get_style(self):
        """获取用户选择的文风模式：tomato（番茄）或 standard（标准）"""
        text = self.style_combo.currentText()
        return "tomato" if "番茄" in text else "standard"


class ApiSettingsDialog(QDialog, FramelessWindowMixin):
    """
    API 设置对话框 - 配置 AI 模型的 API 密钥和运行参数
    功能：
    - 配置 DeepSeek、通义千问、Kimi 三个 API Key
    - 选择路由策略（极速/平衡/质量优先）
    - 选择主写模型偏好
    - 启用/禁用 CrewAI 长期记忆功能
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(Sizes.DIALOG_WIDTH_MD)

        keys = load_api_keys()
        self._current_project = None  # 可由调用方设置，用于清理 Memory

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
        content_layout.setContentsMargins(20, 8, 20, 20)
        content_layout.setSpacing(8)

        header = QLabel("API 设置")
        header.setObjectName("PageTitle")
        content_layout.addWidget(header)

        desc = QLabel("配置 AI 模型的 API 密钥和运行参数")
        desc.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-size: {Typography.CAPTION['size']};")
        content_layout.addWidget(desc)

        form = QFormLayout()
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft)

        self.deepseek = QLineEdit(keys.get("DEEPSEEK_API_KEY", ""))
        self.qwen = QLineEdit(keys.get("DASHSCOPE_API_KEY", ""))
        self.kimi = QLineEdit(keys.get("MOONSHOT_API_KEY", ""))

        for field in [self.deepseek, self.qwen, self.kimi]:
            field.setEchoMode(QLineEdit.Password)
            field.setClearButtonEnabled(False)
            field.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
            field.setPlaceholderText("sk-...")

        self.route_profile = QComboBox()
        self._route_map = {
            "speed": "极速模式",
            "balanced": "平衡模式",
            "quality": "质量优先"
        }
        self._route_map_rev = {v: k for k, v in self._route_map.items()}

        self.route_profile.addItems(list(self._route_map.values()))
        self.route_profile.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)

        route_val = keys.get("ROUTE_PROFILE", "speed")
        if route_val not in self._route_map:
            route_val = "speed"
        self.route_profile.setCurrentText(self._route_map[route_val])

        self.writer_model = QComboBox()
        self.writer_model.addItems(["auto", "qwen", "kimi"])
        self.writer_model.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
        writer_val = keys.get("WRITER_MODEL", "auto")
        if writer_val in ["auto", "qwen", "kimi"]:
            self.writer_model.setCurrentText(writer_val)

        form.addRow("DeepSeek Key", self.deepseek)
        form.addRow("通义千问 Key", self.qwen)
        form.addRow("Kimi Key", self.kimi)
        form.addRow("路由策略", self.route_profile)
        form.addRow("主写模型", self.writer_model)
        content_layout.addLayout(form)

        memory_group = QGroupBox("长期记忆管理")
        memory_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: {Typography.BODY['size']};
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: {Radius.MD};
                margin-top: 12px;
                margin-bottom: 8px;
                padding-top: 8px;
                padding-bottom: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                background: {Colors.WHITE};
            }}
        """)
        memory_layout = QVBoxLayout(memory_group)
        memory_layout.setSpacing(8)

        self.memory_check = QCheckBox("启用长期记忆（跨章节向量检索，需要通义千问 Key + lancedb）")
        self.memory_check.setChecked(bool(keys.get("CREWAI_ENABLE_MEMORY", False)))
        memory_layout.addWidget(self.memory_check)

        memory_hint = QLabel("依赖：pip install lancedb  |  向量记忆清理后不可恢复")
        memory_hint.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-size: {Typography.CAPTION['size']};")
        memory_layout.addWidget(memory_hint)

        self.clear_memory_btn = QPushButton("清理当前项目的 Memory 数据")
        self.clear_memory_btn.setObjectName("DangerButton")
        self.clear_memory_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
        self.clear_memory_btn.clicked.connect(self._on_clear_memory)
        memory_layout.addWidget(self.clear_memory_btn)

        content_layout.addWidget(memory_group)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)

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
        self.save_btn.clicked.connect(self.save_settings)

        apply_drop_shadow(self.container, blur_radius=32, y_offset=8, alpha=25)

    def set_current_project(self, project_name: str):
        """由主窗口调用，传入当前打开的项目名称，供清理 Memory 时使用"""
        self._current_project = project_name

    def _on_clear_memory(self):
        """清理当前项目的 CrewAI Memory 数据"""
        if not self._current_project:
            CustomMessageBox.information(self, "提示", "请先打开一个项目，再执行 Memory 清理。")
            return
        reply = CustomMessageBox.question(
            self,
            "确认清理",
            f"确定要清除项目「{self._current_project}」的所有 Memory 数据吗？\n此操作不可撤销。",
        )
        if not reply:
            return
        try:
            from src.generator import clear_project_memory
            success = clear_project_memory(self._current_project)
            if success:
                self.result_label.setText("Memory 数据已清理")
                self.result_label.setProperty("tone", "success")
            else:
                self.result_label.setText("清理失败，请手动删除项目目录下的 .crewai 文件夹")
                self.result_label.setProperty("tone", "danger")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)
            self.result_label.setVisible(True)
        except Exception as exc:
            self.result_label.setText(str(exc))
            self.result_label.setProperty("tone", "danger")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)
            self.result_label.setVisible(True)

    def save_settings(self):
        """保存 API 配置到加密文件"""
        try:
            selected_text = self.route_profile.currentText()
            route_key = self._route_map_rev.get(selected_text, "speed")

            keys = load_api_keys()
            current_auth = keys.get("AUTH_CODE", "")

            save_api_keys(
                self.deepseek.text().strip(),
                self.qwen.text().strip(),
                self.kimi.text().strip(),
                current_auth,
                route_key,
                self.writer_model.currentText(),
                keys.get("MODEL_PRESET", "default"),
                keys.get("MODEL_PARAMS_BY_ROLE", {}),
                keys.get("MODEL_DEFAULTS_BY_ROLE", {}),
                memory_enabled=self.memory_check.isChecked(),
            )
            self.result_label.setText("配置已保存")
            self.result_label.setProperty("tone", "success")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)
            self.result_label.setVisible(True)
            QThread.msleep(300)
            self.accept()

        except Exception as exc:
            self.result_label.setText(str(exc))
            self.result_label.setVisible(True)
            self.result_label.setProperty("tone", "danger")
            self.result_label.style().unpolish(self.result_label)
            self.result_label.style().polish(self.result_label)


class ModelParamsDialog(QDialog, FramelessWindowMixin):
    """
    模型参数对话框 - 配置各角色 Agent 的模型参数
    功能：
    - 选择参数模式（默认/自定义）
    - 按角色配置 Temperature、Top P、Max Tokens
    - 动态显示当前模型的参数范围
    """
    PRESET_LABELS = {
        "default": "默认模式",
        "custom": "自定义",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(Sizes.DIALOG_WIDTH_MD)
        self._updating_ui = False
        keys = load_api_keys()
        self._keys_cache = keys
        self._role_models = resolve_runtime_role_models(keys)
        self._params_by_role = keys.get("MODEL_PARAMS_BY_ROLE", {})
        self._defaults_by_role = keys.get("MODEL_DEFAULTS_BY_ROLE", {})
        self._current_role = "outline"

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
        content_layout.setContentsMargins(20, 8, 20, 20)
        content_layout.setSpacing(8)

        header = QLabel("模型参数设置")
        header.setObjectName("PageTitle")
        content_layout.addWidget(header)

        form = QFormLayout()
        form.setVerticalSpacing(10)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems(
            [
                self.PRESET_LABELS["default"],
                self.PRESET_LABELS["custom"],
            ]
        )
        self.preset_combo.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
        form.addRow("参数模式", self.preset_combo)

        self.role_combo = QComboBox()
        self._role_display_to_key = {}
        for role in MODEL_ROLES:
            display = MODEL_ROLE_LABELS.get(role, role)
            self._role_display_to_key[display] = role
            self.role_combo.addItem(display)
        self.role_combo.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
        form.addRow("角色选择", self.role_combo)

        self.model_info = QLabel("")
        self.model_info.setObjectName("MutedText")
        self.model_info.setWordWrap(True)
        form.addRow("当前模型", self.model_info)

        temp_row, self.slider_temperature, self.lbl_temperature_value = self._build_slider_row(0, 200, 10, "0.70")
        form.addRow("Temperature", temp_row)

        top_p_row, self.slider_top_p, self.lbl_top_p_value = self._build_slider_row(10, 100, 5, "0.90")
        form.addRow("Top P", top_p_row)

        self.max_tokens_edit = QLineEdit()
        self.max_tokens_edit.setPlaceholderText("留空表示使用模型默认")
        self.max_tokens_edit.setClearButtonEnabled(False)
        self.max_tokens_edit.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)
        form.addRow("Max Tokens", self.max_tokens_edit)

        self.range_hint = QLabel("")
        self.range_hint.setObjectName("MutedText")
        self.range_hint.setWordWrap(True)

        hint = QLabel("提示：修改任意参数后将自动切换为「自定义」模式；可按角色分别保存。")
        hint.setObjectName("MutedText")
        hint.setWordWrap(True)

        content_layout.addLayout(form)
        content_layout.addWidget(self.range_hint)
        content_layout.addWidget(hint)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
        self.save_btn = QPushButton("保存参数")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        content_layout.addLayout(btn_layout)

        container_layout.addWidget(content)

        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self.save_settings)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        self.role_combo.currentIndexChanged.connect(self.on_role_changed)
        self.slider_temperature.valueChanged.connect(self.on_param_edited)
        self.slider_top_p.valueChanged.connect(self.on_param_edited)
        self.max_tokens_edit.textChanged.connect(self.on_param_edited)

        preset_val = keys.get("MODEL_PRESET", "default")
        if preset_val not in {"default", "custom"}:
            preset_val = "default"
        self.set_preset_combo(preset_val)
        self.on_role_changed()

        apply_drop_shadow(self.container, blur_radius=32, y_offset=8, alpha=25)

    def _build_slider_row(self, min_value, max_value, step, default_text):
        """构建滑块行组件：滑块 + 数值显示标签"""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setSingleStep(step)
        slider.setPageStep(step)
        slider.setMinimumHeight(32)
        value_label = QLabel(default_text)
        value_label.setFixedWidth(48)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(slider, 1)
        layout.addWidget(value_label)
        return row, slider, value_label

    def set_preset_combo(self, preset_key):
        """设置预设模式下拉框的当前值"""
        label = self.PRESET_LABELS.get(preset_key, self.PRESET_LABELS["default"])
        self._updating_ui = True
        self.preset_combo.setCurrentText(label)
        self._updating_ui = False

    def _collect_params(self):
        """收集当前 UI 中的参数值"""
        max_tokens_text = self.max_tokens_edit.text().strip()
        max_tokens = None
        if max_tokens_text:
            try:
                max_tokens = int(max_tokens_text)
                if max_tokens <= 0:
                    max_tokens = None
            except ValueError:
                max_tokens = None
        return {
            "temperature": round(self.slider_temperature.value() / 100.0, 2),
            "top_p": round(self.slider_top_p.value() / 100.0, 2),
            "max_tokens": max_tokens,
        }

    def _current_role_limits(self):
        """获取当前角色所用模型的能力边界"""
        model_name = self._role_models.get(self._current_role, "")
        return get_model_capability_limits(model_name)

    def _sync_dynamic_ranges(self):
        """同步滑块的动态范围（根据模型能力边界）"""
        limits = self._current_role_limits()
        t_min = int(round(float(limits["temperature"]["min"]) * 100))
        t_max = int(round(float(limits["temperature"]["max"]) * 100))
        t_step = max(1, int(round(float(limits["temperature"]["step"]) * 100)))
        p_min = int(round(float(limits["top_p"]["min"]) * 100))
        p_max = int(round(float(limits["top_p"]["max"]) * 100))
        p_step = max(1, int(round(float(limits["top_p"]["step"]) * 100)))

        self.slider_temperature.setRange(t_min, t_max)
        self.slider_temperature.setSingleStep(t_step)
        self.slider_temperature.setPageStep(t_step)
        self.slider_top_p.setRange(p_min, p_max)
        self.slider_top_p.setSingleStep(p_step)
        self.slider_top_p.setPageStep(p_step)
        model_name = self._role_models.get(self._current_role, "unknown")
        self.model_info.setText(model_name)
        self.range_hint.setText(
            f"动态范围（{model_name}）："
            f"Temperature {limits['temperature']['min']:.1f}-{limits['temperature']['max']:.1f}，"
            f"Top P {limits['top_p']['min']:.1f}-{limits['top_p']['max']:.1f}，"
            f"Max Tokens {int(limits['max_tokens']['min'])}-{int(limits['max_tokens']['max'])}"
        )

    def _params_for_role(self, role):
        """获取指定角色的参数（根据预设模式选择来源）"""
        selected_label = self.preset_combo.currentText()
        preset_key = "default" if selected_label == self.PRESET_LABELS["default"] else "custom"
        source = self._defaults_by_role if preset_key == "default" else self._params_by_role
        return source.get(role, {"temperature": 0.7, "top_p": 0.9, "max_tokens": None})

    def apply_params_to_ui(self, params):
        """将参数应用到 UI 控件"""
        self._updating_ui = True
        self.slider_temperature.setValue(int(round(float(params.get("temperature", 0.7)) * 100)))
        self.slider_top_p.setValue(int(round(float(params.get("top_p", 0.9)) * 100)))
        max_tokens = params.get("max_tokens", None)
        self.max_tokens_edit.setText("" if max_tokens in (None, "") else str(max_tokens))
        self._updating_ui = False
        self._sync_slider_labels()

    def _sync_slider_labels(self):
        """同步滑块标签显示当前值"""
        self.lbl_temperature_value.setText(f"{self.slider_temperature.value() / 100.0:.2f}")
        self.lbl_top_p_value.setText(f"{self.slider_top_p.value() / 100.0:.2f}")

    def on_preset_changed(self):
        """预设模式切换时的处理"""
        if self._updating_ui:
            return
        self._sync_dynamic_ranges()
        self.apply_params_to_ui(self._params_for_role(self._current_role))

    def on_role_changed(self):
        """角色切换时的处理"""
        if self._updating_ui:
            return
        role_display = self.role_combo.currentText()
        self._current_role = self._role_display_to_key.get(role_display, "outline")
        self._sync_dynamic_ranges()
        self.apply_params_to_ui(self._params_for_role(self._current_role))

    def on_param_edited(self):
        """参数编辑时的处理：自动切换到自定义模式"""
        if self._updating_ui:
            return
        self._sync_slider_labels()
        self._params_by_role[self._current_role] = self._collect_params()
        if self.preset_combo.currentText() != self.PRESET_LABELS["custom"]:
            self.set_preset_combo("custom")

    def save_settings(self):
        """保存模型参数配置"""
        keys = load_api_keys()
        selected_label = self.preset_combo.currentText()
        key_map = {v: k for k, v in self.PRESET_LABELS.items()}
        preset_key = key_map.get(selected_label, "default")
        save_api_keys(
            keys.get("DEEPSEEK_API_KEY", ""),
            keys.get("DASHSCOPE_API_KEY", ""),
            keys.get("MOONSHOT_API_KEY", ""),
            keys.get("AUTH_CODE", ""),
            keys.get("ROUTE_PROFILE", "speed"),
            keys.get("WRITER_MODEL", "auto"),
            preset_key,
            self._params_by_role,
            self._defaults_by_role,
        )
        self.accept()


class LicenseSettingsDialog(QDialog, FramelessWindowMixin):
    """
    授权管理对话框 - 验证和管理软件授权
    功能：
    - 显示机器码
    - 输入并验证授权码
    - 显示授权状态和有效期
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_frameless("", translucent=True)
        self.setModal(True)
        self.setMinimumWidth(Sizes.DIALOG_WIDTH_SM)

        keys = load_api_keys()
        from src.license import license_manager

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
        content_layout.setContentsMargins(20, 8, 20, 20)
        content_layout.setSpacing(8)

        header = QLabel("系统授权管理")
        header.setObjectName("PageTitle")
        content_layout.addWidget(header)

        desc = QLabel("验证授权码以激活软件完整功能")
        desc.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-size: {Typography.CAPTION['size']};")
        content_layout.addWidget(desc)

        form = QFormLayout()
        form.setVerticalSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft)

        self.machine_code_display = QLineEdit(license_manager.get_machine_code())
        self.machine_code_display.setReadOnly(True)
        self.machine_code_display.setClearButtonEnabled(False)
        self.machine_code_display.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)

        self.auth_code = QLineEdit(keys.get("AUTH_CODE", ""))
        self.auth_code.setPlaceholderText("请输入授权码...")
        self.auth_code.setClearButtonEnabled(False)
        self.auth_code.setMinimumHeight(Sizes.INPUT_HEIGHT_MD)

        form.addRow("机器码", self.machine_code_display)
        form.addRow("授权码", self.auth_code)

        content_layout.addLayout(form)

        self.license_status_label = QLabel("未验证")
        self.license_status_label.setStyleSheet(f"color: {Colors.TEXT_TERTIARY}; font-weight: {Typography.WEIGHT_SEMIBOLD}; font-size: {Typography.CAPTION['size']};")
        self.license_status_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.license_status_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)

        self.btn_verify = QPushButton("验证授权")
        self.btn_verify.setObjectName("PrimaryButton")
        self.btn_verify.setMinimumHeight(Sizes.BUTTON_HEIGHT_LG)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.btn_verify)

        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content)

        self.cancel_btn.clicked.connect(self.reject)
        self.btn_verify.clicked.connect(self.verify_and_save)

        apply_drop_shadow(self.container, blur_radius=32, y_offset=8, alpha=25)

        if self.auth_code.text().strip():
            self._do_verify(self.auth_code.text().strip())

    def _do_verify(self, code):
        """执行授权验证"""
        from src.license import license_manager
        result = license_manager.verify_license(code)
        if result["valid"]:
            expires_at = result.get("expires_at", "未知")[:10] if result.get("expires_at") else "永久"
            self.license_status_label.setText(f"验证通过 (有效期至: {expires_at})")
            self.license_status_label.setStyleSheet(f"color: {Colors.SUCCESS_600}; font-weight: {Typography.WEIGHT_SEMIBOLD}; font-size: {Typography.BODY['size']};")
            return True
        else:
            self.license_status_label.setText(result['message'])
            self.license_status_label.setStyleSheet(f"color: {Colors.ERROR_600}; font-weight: {Typography.WEIGHT_SEMIBOLD}; font-size: {Typography.BODY['size']};")
            return False

    def verify_and_save(self):
        """验证并保存授权码"""
        code = self.auth_code.text().strip()
        if not code:
            self.license_status_label.setText("请输入授权码")
            self.license_status_label.setStyleSheet(f"color: {Colors.ERROR_600}; font-weight: {Typography.WEIGHT_SEMIBOLD}; font-size: {Typography.BODY['size']};")
            return

        is_valid = self._do_verify(code)
        if is_valid:
            keys = load_api_keys()
            save_api_keys(
                keys.get("DEEPSEEK_API_KEY", ""),
                keys.get("DASHSCOPE_API_KEY", ""),
                keys.get("MOONSHOT_API_KEY", ""),
                code,
                keys.get("ROUTE_PROFILE", "speed"),
                keys.get("WRITER_MODEL", "auto"),
                keys.get("MODEL_PRESET", "default"),
                keys.get("MODEL_PARAMS_BY_ROLE", {}),
                keys.get("MODEL_DEFAULTS_BY_ROLE", {}),
            )
            QThread.msleep(500)
            self.accept()
