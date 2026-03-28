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
    padding: 0px;
}}

QComboBox::down-arrow {{
    width: 0px;
    height: 0px;
    image: none;
    border: none;
    background: none;
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
"""
