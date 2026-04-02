from .variables import Colors, Typography, Spacing, Radius, Shadows, Transitions, Sizes

COMPONENT_STYLES = f"""
QPushButton {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 0 12px;
    min-height: {Sizes.BUTTON_HEIGHT_MD}px;
    min-width: {Sizes.BUTTON_MIN_WIDTH}px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton:hover {{
    background-color: {Colors.GRAY_50};
    border-color: {Colors.GRAY_300};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton:pressed {{
    background-color: {Colors.GRAY_100};
}}

QPushButton:disabled {{
    background-color: {Colors.GRAY_50};
    color: {Colors.TEXT_MUTED};
    border-color: {Colors.BORDER_LIGHT};
}}

QPushButton#PrimaryButton {{
    background-color: {Colors.PRIMARY_500};
    border: none;
    color: {Colors.WHITE};
    font-weight: {Typography.WEIGHT_MEDIUM};
}}

QPushButton#PrimaryButton:hover {{
    background-color: {Colors.PRIMARY_600};
}}

QPushButton#PrimaryButton:pressed {{
    background-color: {Colors.PRIMARY_700};
}}

QPushButton#PrimaryButton:disabled {{
    background-color: {Colors.PRIMARY_200};
    color: {Colors.WHITE};
}}

QPushButton#DangerButton {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.ERROR_100};
    color: {Colors.ERROR_600};
}}

QPushButton#DangerButton:hover {{
    background-color: {Colors.ERROR_50};
    border-color: {Colors.ERROR_300};
}}

QPushButton#DangerButton:pressed {{
    background-color: {Colors.ERROR_100};
}}

QPushButton#IconButton {{
    background-color: transparent;
    border: none;
    border-radius: {Radius.SM};
    min-width: 24px;
    min-height: 24px;
    padding: 0;
    font-size: 14px;
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton#IconButton:hover {{
    background-color: {Colors.GRAY_100};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton#IconButtonDanger {{
    background-color: transparent;
    border: none;
    border-radius: {Radius.SM};
    min-width: 24px;
    min-height: 24px;
    padding: 0;
    font-size: 14px;
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton#IconButtonDanger:hover {{
    background-color: {Colors.ERROR_50};
    color: {Colors.ERROR_500};
}}

QPushButton#IconButtonDanger:pressed {{
    background-color: {Colors.ERROR_100};
}}

QPushButton#SegmentedButton {{
    background: transparent;
    border: 1px solid transparent;
    color: {Colors.TEXT_SECONDARY};
    font-size: 11px;
    font-weight: {Typography.WEIGHT_MEDIUM};
    padding: 3px 10px;
    min-height: 22px;
    border-radius: {Radius.SM};
}}

QPushButton#SegmentedButton:checked {{
    background: {Colors.WHITE};
    border-color: {Colors.BORDER};
    color: {Colors.PRIMARY_500};
    box-shadow: {Shadows.SM};
}}

QPushButton#SegmentedButton:hover:!checked {{
    background: rgba(255, 255, 255, 0.5);
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton#SegmentedButton:checked:hover {{
    background: {Colors.GRAY_50};
    border-color: {Colors.GRAY_300};
}}

QPushButton#SecondaryButton {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton#SecondaryButton:hover {{
    background-color: {Colors.GRAY_50};
    border-color: {Colors.GRAY_300};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton#SecondaryButton:pressed {{
    background-color: {Colors.GRAY_100};
}}

QPushButton#TitleBarButton {{
    background-color: transparent;
    border: none;
    border-radius: {Radius.SM};
    min-width: 28px;
    min-height: 24px;
    padding: 0;
    font-size: 12px;
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton#TitleBarButton:hover {{
    background-color: {Colors.GRAY_100};
}}

QPushButton#TitleBarCloseButton {{
    background-color: transparent;
    border: none;
    border-radius: {Radius.SM};
    min-width: 28px;
    min-height: 24px;
    padding: 0;
    font-size: 12px;
    color: {Colors.TEXT_SECONDARY};
}}

QPushButton#TitleBarCloseButton:hover {{
    background-color: {Colors.ERROR_500};
    color: {Colors.WHITE};
}}

QLineEdit {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 0 10px;
    min-height: {Sizes.INPUT_HEIGHT_MD}px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.PRIMARY_100};
}}

QLineEdit:hover {{
    border-color: {Colors.GRAY_300};
}}

QLineEdit:focus {{
    border-color: {Colors.PRIMARY_500};
    border-width: 1px;
}}

QLineEdit:disabled {{
    background-color: {Colors.GRAY_50};
    color: {Colors.TEXT_MUTED};
}}

QLineEdit::placeholder {{
    color: {Colors.TEXT_MUTED};
}}

QLineEdit::clear-button {{
    width: 0px;
    height: 0px;
    margin: 0px;
    padding: 0px;
    border: none;
    background: transparent;
    image: none;
}}

QLineEdit[echoMode="2"] {{
    lineedit-password-character: 9679;
}}

QLineEdit::peek-button {{
    width: 0px;
    height: 0px;
    margin: 0px;
    padding: 0px;
    border: none;
    background: transparent;
    image: none;
}}

QLineEdit::spin-button {{
    width: 0px;
    height: 0px;
    margin: 0px;
    padding: 0px;
    border: none;
    background: transparent;
    image: none;
}}

QTextEdit {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: {Radius.LG};
    padding: 8px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.PRIMARY_100};
}}

QTextEdit:focus {{
    border-color: {Colors.PRIMARY_300};
}}

QTextEdit#MarkdownEditor {{
    border: none;
    background-color: {Colors.SURFACE};
}}

QPlainTextEdit#MarkdownEditor {{
    border: none;
    background-color: {Colors.SURFACE};
    padding: 8px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.PRIMARY_100};
}}

QTextEdit#ReaderContent {{
    border: none;
    background-color: {Colors.SURFACE};
    padding: 16px 24px;
    line-height: 1.8;
}}

QTextEdit#LogViewer {{
    background-color: {Colors.GRAY_900};
    border: none;
    border-radius: 0;
    padding: 12px;
    color: {Colors.GRAY_300};
    font-family: 'Consolas', 'Microsoft YaHei Mono', monospace;
    font-size: {Typography.CAPTION['size']};
}}

QComboBox {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 0 10px;
    padding-right: 28px;
    min-height: {Sizes.INPUT_HEIGHT_MD}px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QComboBox:hover {{
    border-color: {Colors.GRAY_300};
}}

QComboBox:focus {{
    border-color: {Colors.PRIMARY_500};
}}

QComboBox:disabled {{
    background-color: {Colors.GRAY_50};
    color: {Colors.TEXT_MUTED};
}}

QComboBox::drop-down {{
    border: none;
    width: 0px;
    background: transparent;
}}

QComboBox::down-arrow {{
    image: none;
    width: 0px;
    height: 0px;
    border: none;
}}

QComboBox::down-arrow:on {{
    border-top: none;
    border-bottom: 6px solid {Colors.TEXT_SECONDARY};
}}

QComboBox:hover::down-arrow {{
    border-top-color: {Colors.TEXT_PRIMARY};
}}

QComboBox:hover::down-arrow:on {{
    border-bottom-color: {Colors.TEXT_PRIMARY};
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 4px;
    selection-background-color: {Colors.PRIMARY_50};
    selection-color: {Colors.PRIMARY_700};
    outline: none;
    alternate-background-color: {Colors.SURFACE};
}}

QComboBox QAbstractItemView::item {{
    background-color: {Colors.SURFACE};
    min-height: 28px;
    padding: 0 8px;
    border-radius: {Radius.SM};
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {Colors.GRAY_50};
}}

QComboBox QAbstractItemView::item:selected {{
    background-color: {Colors.PRIMARY_50};
    color: {Colors.PRIMARY_700};
}}

QSpinBox {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 0 8px;
    padding-right: 0px;
    min-height: {Sizes.INPUT_HEIGHT_MD}px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QSpinBox:hover {{
    border-color: {Colors.GRAY_300};
}}

QSpinBox:focus {{
    border-color: {Colors.PRIMARY_500};
}}

QSpinBox::up-button,
QSpinBox::down-button {{
    background-color: transparent;
    border: none;
    width: 0px;
    height: 0px;
    padding: 0px;
}}

QSpinBox::up-arrow {{
    width: 0px;
    height: 0px;
    image: none;
    border: none;
    background: none;
}}

QSpinBox::down-arrow {{
    width: 0px;
    height: 0px;
    image: none;
    border: none;
    background: none;
}}

QSpinBox::up-button:subcontrol-origin {{
    margin: 0px;
    padding: 0px;
}}

QSpinBox::down-button:subcontrol-origin {{
    margin: 0px;
    padding: 0px;
}}

QSlider::groove:horizontal {{
    background-color: {Colors.GRAY_200};
    height: 4px;
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background-color: {Colors.PRIMARY_500};
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {Colors.PRIMARY_600};
}}

QSlider::handle:horizontal:disabled {{
    background-color: {Colors.GRAY_300};
}}

QRadioButton {{
    spacing: 8px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {Colors.BORDER};
    border-radius: 8px;
    background-color: {Colors.SURFACE};
}}

QRadioButton::indicator:hover {{
    border-color: {Colors.PRIMARY_300};
}}

QRadioButton::indicator:checked {{
    border-color: {Colors.PRIMARY_500};
    background-color: {Colors.SURFACE};
    border-width: 5px;
}}

QCheckBox {{
    spacing: 8px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {Colors.BORDER};
    border-radius: {Radius.SM};
    background-color: {Colors.SURFACE};
}}

QCheckBox::indicator:hover {{
    border-color: {Colors.PRIMARY_300};
}}

QCheckBox::indicator:checked {{
    background-color: {Colors.PRIMARY_500};
    border-color: {Colors.PRIMARY_500};
}}

QProgressBar {{
    background-color: {Colors.GRAY_200};
    border: none;
    border-radius: 3px;
    height: 6px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {Colors.PRIMARY_500};
    border-radius: 3px;
}}

QGroupBox {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: {Radius.LG};
    margin-top: 16px;
    padding-top: 12px;
    font-weight: {Typography.WEIGHT_MEDIUM};
    font-size: {Typography.BODY_SMALL['size']};
    color: {Colors.TEXT_SECONDARY};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
    background-color: {Colors.SURFACE};
}}

QFormLayout {{
    spacing: 12px;
}}

/* ===== 侧边栏专用样式 ===== */

/* 侧边栏容器 */
QFrame#Sidebar {{
    background-color: {Colors.SURFACE};
    border-right: 1px solid {Colors.BORDER};
}}

/* 侧边栏头部 */
QWidget#SidebarHeader {{
    background-color: {Colors.SURFACE};
    border-bottom: 1px solid {Colors.BORDER};
}}

/* Logo容器 */
QWidget#LogoContainer {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {Colors.PRIMARY_500}, stop:1 {Colors.PURPLE_500});
    border-radius: {Radius.MD};
}}

QLabel#LogoText {{
    color: {Colors.WHITE};
    font-size: 12px;
    font-weight: {Typography.WEIGHT_BOLD};
}}

/* 品牌标题 */
QLabel#BrandTitle {{
    font-size: 15px;
    font-weight: {Typography.WEIGHT_SEMIBOLD};
    color: {Colors.TEXT_PRIMARY};
}}

/* 版本号 */
QLabel#VersionText {{
    font-size: 11px;
    color: {Colors.TEXT_MUTED};
}}

/* 侧边栏内容区 */
QWidget#SidebarContent {{
    background-color: {Colors.SURFACE};
}}

/* 分组标签 */
QLabel#SectionLabel {{
    font-size: 11px;
    font-weight: {Typography.WEIGHT_SEMIBOLD};
    color: {Colors.TEXT_MUTED};
    text-transform: uppercase;
    margin-bottom: 8px;
    margin-top: 16px;
}}

QLabel#SectionLabel:first-of-type {{
    margin-top: 0;
}}

/* 项目选择器 */
QComboBox#ProjectSelector {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG};
    padding: 0 12px;
    padding-right: 28px;
    min-height: 42px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QComboBox#ProjectSelector:hover {{
    border-color: {Colors.PRIMARY_400};
}}

QComboBox#ProjectSelector:focus {{
    border-color: {Colors.PRIMARY_500};
    border-width: 1px;
}}

/* 文风选择器 */
QComboBox#StyleSelector {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG};
    padding: 0 12px;
    padding-right: 28px;
    min-height: 40px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QComboBox#StyleSelector:hover {{
    border-color: {Colors.PRIMARY_400};
}}

/* 小型主按钮 */
QPushButton#PrimaryButtonSmall {{
    background-color: {Colors.PRIMARY_500};
    border: none;
    border-radius: {Radius.MD};
    color: {Colors.WHITE};
    font-size: {Typography.BODY_SMALL['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    min-height: 36px;
    padding: 0 16px;
}}

QPushButton#PrimaryButtonSmall:hover {{
    background-color: {Colors.PRIMARY_600};
}}

QPushButton#PrimaryButtonSmall:pressed {{
    background-color: {Colors.PRIMARY_700};
}}

/* 危险图标按钮 */
QPushButton#DangerIconButton {{
    background-color: transparent;
    border: 1px solid {Colors.ERROR_200};
    border-radius: {Radius.MD};
    color: {Colors.ERROR_500};
    font-size: 14px;
    min-width: 36px;
    min-height: 36px;
    max-width: 36px;
    max-height: 36px;
    padding: 0;
}}

QPushButton#DangerIconButton:hover {{
    background-color: {Colors.ERROR_50};
    border-color: {Colors.ERROR_500};
}}

QPushButton#DangerIconButton:pressed {{
    background-color: {Colors.ERROR_100};
}}

/* 设置容器 */
QWidget#SettingsContainer {{
    background-color: transparent;
    margin-top: 8px;
}}

/* 分隔线 */
QWidget#DividerLine {{
    background-color: {Colors.BORDER};
    max-height: 1px;
}}

QLabel#DividerText {{
    font-size: 11px;
    font-weight: {Typography.WEIGHT_SEMIBOLD};
    color: {Colors.TEXT_MUTED};
    text-transform: uppercase;
    padding: 0 8px;
}}

/* 设置项 */
QPushButton#SettingItem {{
    background-color: transparent;
    border: none;
    border-radius: {Radius.MD};
    color: {Colors.TEXT_SECONDARY};
    font-size: {Typography.BODY_SMALL['size']};
    text-align: left;
    padding: 0 12px;
    min-height: 38px;
}}

QPushButton#SettingItem:hover {{
    background-color: {Colors.GRAY_100};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton#SettingItem:pressed {{
    background-color: {Colors.GRAY_200};
}}

/* 底部文字 */
QLabel#FooterText {{
    font-size: 11px;
    color: {Colors.TEXT_MUTED};
    margin-top: 16px;
}}

/* 终端/日志查看器 */
QTextEdit#LogViewer {{
    background-color: #1E1E1E;
    color: #E5E7EB;
    border: none;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.6;
    padding: 16px;
}}

QFrame#CardHeader {{
    background-color: {Colors.GRAY_50};
    border-bottom: 1px solid {Colors.BORDER};
}}

/* 标签页样式 */
QTabWidget::pane {{
    border: none;
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {Colors.TEXT_SECONDARY};
    padding: 10px 20px;
    margin-right: 4px;
    border-radius: {Radius.LG};
    font-size: {Typography.BODY['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
}}

QTabBar::tab:hover {{
    background-color: {Colors.GRAY_100};
    color: {Colors.TEXT_PRIMARY};
}}

QTabBar::tab:selected {{
    background-color: {Colors.PRIMARY_50};
    color: {Colors.PRIMARY_600};
    font-weight: {Typography.WEIGHT_SEMIBOLD};
}}

/* ===== 弹窗对话框专用样式 ===== */

/* 弹窗容器 */
QFrame#DialogContainer {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.XL2};
}}

/* 弹窗标题 */
QLabel#PageTitle {{
    font-size: {Typography.H3['size']};
    font-weight: {Typography.WEIGHT_BOLD};
    color: {Colors.TEXT_PRIMARY};
    margin-bottom: 4px;
}}

/* 弹窗描述文字 */
QLabel#DialogDescription {{
    font-size: {Typography.CAPTION['size']};
    color: {Colors.TEXT_TERTIARY};
    margin-bottom: 16px;
}}

/* 弹窗主按钮 */
QDialog QPushButton#PrimaryButton {{
    background-color: {Colors.PRIMARY_500};
    border: none;
    border-radius: {Radius.MD};
    color: {Colors.WHITE};
    font-size: {Typography.BODY['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    min-height: {Sizes.BUTTON_HEIGHT_LG}px;
    padding: 0 24px;
}}

QDialog QPushButton#PrimaryButton:hover {{
    background-color: {Colors.PRIMARY_600};
}}

QDialog QPushButton#PrimaryButton:pressed {{
    background-color: {Colors.PRIMARY_700};
}}

/* 弹窗次要按钮 */
QDialog QPushButton#SecondaryButton {{
    background-color: transparent;
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    color: {Colors.TEXT_SECONDARY};
    font-size: {Typography.BODY['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    min-height: {Sizes.BUTTON_HEIGHT_LG}px;
    padding: 0 24px;
}}

QDialog QPushButton#SecondaryButton:hover {{
    background-color: {Colors.GRAY_50};
    border-color: {Colors.GRAY_300};
    color: {Colors.TEXT_PRIMARY};
}}

QDialog QPushButton#SecondaryButton:pressed {{
    background-color: {Colors.GRAY_100};
}}

/* 弹窗危险按钮 */
QDialog QPushButton#DangerButton {{
    background-color: transparent;
    border: 1px solid {Colors.ERROR_200};
    border-radius: {Radius.MD};
    color: {Colors.ERROR_500};
    font-size: {Typography.BODY['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    min-height: {Sizes.BUTTON_HEIGHT_LG}px;
    padding: 0 24px;
}}

QDialog QPushButton#DangerButton:hover {{
    background-color: {Colors.ERROR_50};
    border-color: {Colors.ERROR_500};
}}

/* 弹窗输入框 */
QDialog QLineEdit {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 0 12px;
    min-height: {Sizes.INPUT_HEIGHT_MD}px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QDialog QLineEdit:hover {{
    border-color: {Colors.GRAY_300};
}}

QDialog QLineEdit:focus {{
    border-color: {Colors.PRIMARY_500};
}}

/* 弹窗下拉框 */
QDialog QComboBox {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.MD};
    padding: 0 12px;
    min-height: {Sizes.INPUT_HEIGHT_MD}px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QDialog QComboBox:hover {{
    border-color: {Colors.GRAY_300};
}}

QDialog QComboBox:focus {{
    border-color: {Colors.PRIMARY_500};
}}

/* 弹窗表单标签 */
QDialog QFormLayout QLabel {{
    font-size: {Typography.BODY_SMALL['size']};
    color: {Colors.TEXT_SECONDARY};
    font-weight: {Typography.WEIGHT_MEDIUM};
}}

/* 弹窗分组框 */
QDialog QGroupBox {{
    background-color: {Colors.GRAY_50};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG};
    margin-top: 16px;
    padding-top: 12px;
    padding-bottom: 12px;
    font-size: {Typography.BODY_SMALL['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    color: {Colors.TEXT_SECONDARY};
}}

QDialog QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background: {Colors.GRAY_50};
}}

/* 弹窗滑块 */
QDialog QSlider::groove:horizontal {{
    background-color: {Colors.GRAY_200};
    height: 4px;
    border-radius: 2px;
}}

QDialog QSlider::handle:horizontal {{
    background-color: {Colors.PRIMARY_500};
    border: none;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}

QDialog QSlider::handle:horizontal:hover {{
    background-color: {Colors.PRIMARY_600};
}}

/* 弹窗复选框 */
QDialog QCheckBox {{
    spacing: 8px;
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QDialog QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {Colors.BORDER};
    border-radius: {Radius.SM};
    background-color: {Colors.SURFACE};
}}

QDialog QCheckBox::indicator:hover {{
    border-color: {Colors.PRIMARY_300};
}}

QDialog QCheckBox::indicator:checked {{
    background-color: {Colors.PRIMARY_500};
    border-color: {Colors.PRIMARY_500};
}}

/* 提示横幅 */
QLabel#Banner {{
    padding: 12px 16px;
    border-radius: {Radius.MD};
    font-size: {Typography.BODY_SMALL['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
}}

QLabel#Banner[tone="info"] {{
    background-color: {Colors.PRIMARY_50};
    color: {Colors.PRIMARY_600};
    border: 1px solid {Colors.PRIMARY_100};
}}

QLabel#Banner[tone="success"] {{
    background-color: {Colors.SUCCESS_50};
    color: {Colors.SUCCESS_600};
    border: 1px solid {Colors.SUCCESS_100};
}}

QLabel#Banner[tone="warning"] {{
    background-color: {Colors.WARNING_50};
    color: {Colors.WARNING_600};
    border: 1px solid {Colors.WARNING_100};
}}

QLabel#Banner[tone="danger"] {{
    background-color: {Colors.ERROR_50};
    color: {Colors.ERROR_600};
    border: 1px solid {Colors.ERROR_100};
}}
"""
