from .variables import Colors, Typography, Spacing, Radius, Shadows, Transitions, Sizes

BASE_STYLES = f"""
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

QWidget {{
    font-family: {Typography.FONT_CHINESE};
    font-size: {Typography.BODY['size']};
    color: {Colors.TEXT_PRIMARY};
}}

QPushButton {{
    cursor: pointer;
}}

QLineEdit, QTextEdit, QPlainTextEdit {{
    cursor: text;
}}

QMainWindow {{
    background-color: {Colors.BACKGROUND};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.GRAY_300};
    border-radius: 4px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {Colors.GRAY_400};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {{
    background-color: transparent;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    margin: 0;
}}

QScrollBar::handle:horizontal {{
    background-color: {Colors.GRAY_300};
    border-radius: 4px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {Colors.GRAY_400};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {{
    background-color: transparent;
}}

QToolTip {{
    background-color: {Colors.GRAY_800};
    color: {Colors.WHITE};
    border: none;
    border-radius: {Radius.SM};
    padding: 4px 8px;
    font-size: {Typography.CAPTION['size']};
}}

QFrame#Card {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: {Radius.XL};
}}

QFrame#Card:hover {{
    border-color: {Colors.BORDER};
}}

QFrame#DialogContainer {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER_LIGHT};
    border-radius: {Radius.XL2};
}}

QLabel#PageTitle {{
    font-size: {Typography.H2['size']};
    font-weight: {Typography.H2['weight']};
    color: {Colors.TEXT_PRIMARY};
}}

QLabel#MutedText {{
    color: {Colors.TEXT_TERTIARY};
    font-size: {Typography.CAPTION['size']};
}}

QLabel#StatValue {{
    font-size: 20px;
    font-weight: {Typography.WEIGHT_BOLD};
    color: {Colors.TEXT_PRIMARY};
}}

QLabel#StatLabel {{
    font-size: {Typography.CAPTION['size']};
    color: {Colors.TEXT_SECONDARY};
}}

QLabel#Banner {{
    padding: 8px 12px;
    border-radius: {Radius.MD};
    font-size: {Typography.CAPTION['size']};
}}

QLabel#Banner[tone="info"] {{
    background-color: {Colors.PRIMARY_50};
    color: {Colors.PRIMARY_700};
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
