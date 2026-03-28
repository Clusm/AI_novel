from .variables import Colors, Typography, Spacing, Radius, Shadows, Transitions, Sizes

LAYOUT_STYLES = f"""
QFrame#Sidebar {{
    background-color: {Colors.SURFACE};
    border-right: 1px solid {Colors.BORDER_LIGHT};
}}

QFrame#MainPanel {{
    background-color: {Colors.BACKGROUND};
}}

QFrame#CentralWidget {{
    background-color: {Colors.BACKGROUND};
    border-radius: {Radius.XL};
}}

QFrame#TitleBar {{
    background-color: {Colors.SURFACE};
    border-bottom: 1px solid {Colors.BORDER_LIGHT};
}}

QLabel#TitleBarLabel {{
    font-size: {Typography.BODY['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    color: {Colors.TEXT_PRIMARY};
}}

QTabWidget::pane {{
    border: none;
    background-color: transparent;
    margin-top: -1px;
}}

QTabBar {{
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 0 16px;
    min-height: {Sizes.TAB_HEIGHT}px;
    font-size: {Typography.BODY['size']};
    font-weight: {Typography.WEIGHT_MEDIUM};
    color: {Colors.TEXT_SECONDARY};
}}

QTabBar::tab:hover {{
    color: {Colors.TEXT_PRIMARY};
    background-color: {Colors.GRAY_50};
}}

QTabBar::tab:selected {{
    color: {Colors.PRIMARY_600};
    border-bottom-color: {Colors.PRIMARY_500};
}}

QSplitter::handle {{
    background-color: {Colors.BORDER_LIGHT};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

QFrame#WelcomeStepCard {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: {Radius.LG};
}}

QFrame#WelcomeStepCard:hover {{
    border-color: {Colors.PRIMARY_300};
    background-color: {Colors.PRIMARY_50};
}}

QFrame#ColorBar {{
    border-top-left-radius: {Radius.LG};
    border-top-right-radius: {Radius.LG};
}}

QWidget#WelcomeWidget {{
    background-color: {Colors.BACKGROUND};
}}
"""
