
APP_STYLESHEET = """
/* =========================================================
   QMessageBox 及标准弹窗定制样式
   修复深色/亮色背景下文字看不清的问题
   ========================================================= */
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #1e293b;
    font-size: 14px;
    font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
}

QMessageBox QPushButton {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    min-width: 80px;
    font-weight: bold;
}

QMessageBox QPushButton:hover {
    background-color: #2563eb;
}

QMessageBox QPushButton:pressed {
    background-color: #1d4ed8;
}

/* 全局设置 */
QWidget {
    color: #1e293b;
    font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
    font-size: 14px;
    outline: none;
}

QMainWindow {
    background: #f1f5f9;
}

QDialog {
    background: transparent;
}

QFrame#DialogContainer {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
}

QFrame#CentralWidget {
    background: #f8fbff;
    border: 1px solid #dbe3ef;
    border-radius: 16px;
}

QWidget#TitleBar {
    background: #f8fbff;
    border-bottom: 1px solid #e2e8f0;
    border-top-right-radius: 10px;
    border-top-left-radius: 0px;
}

QFrame#DialogContainer QWidget#TitleBar {
    background: #ffffff;
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
}

QLabel#TitleBarLabel {
    font-size: 14px;
    font-weight: 700;
    color: #475569;
    padding-left: 12px;
}

QPushButton#TitleBarButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    color: #64748b;
    font-size: 14px;
    padding: 4px;
    margin: 4px;
    width: 28px;
    height: 28px;
}

QPushButton#TitleBarButton:hover {
    background: #e2e8f0;
    color: #334155;
}

QPushButton#TitleBarCloseButton {
    background: transparent;
    border: none;
    border-radius: 4px;
    color: #64748b;
    font-size: 14px;
    padding: 4px;
    margin: 4px;
    width: 28px;
    height: 28px;
}

QPushButton#TitleBarCloseButton:hover {
    background: #fee2e2;
    color: #ef4444;
}

/* 侧边栏样式 */
QFrame#Sidebar {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}

QWidget#MainPanel {
    background: transparent;
}

QLabel#Title {
    font-size: 18px;
    font-weight: 800;
    color: #0f172a;
    padding: 8px 0 2px 0;
    font-family: "Segoe UI", "Microsoft YaHei UI";
}

QLabel#MutedText {
    color: #94a3b8;
    font-weight: 500;
    font-size: 12px;
}

QLabel#FooterText {
    color: #cbd5e1;
    font-size: 11px;
    line-height: 1.4;
}

/* 卡片样式 */
QFrame#Card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}

QFrame#Card[variant="stat"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}

QFrame#Card:hover {
    border: 1px solid #d5e3fb;
}

QFrame#ColorBar {
    border-top-left-radius: 16px;
    border-top-right-radius: 16px;
    min-height: 6px;
    max-height: 6px;
}

/* 统计数字 */
QLabel#StatValue {
    font-size: 32px;
    font-weight: 800;
    color: #0f172a;
    font-family: "Segoe UI", sans-serif;
    margin-top: 8px;
}

QLabel#StatLabel {
    font-size: 13px;
    color: #64748b;
    font-weight: 600;
    margin-bottom: 8px;
}

/* 标题 */
QLabel#PageTitle {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}

/* Banner / Badge */
QLabel#Banner {
    border-radius: 8px;
    padding: 10px 14px;
    font-weight: 500;
}

QLabel#Banner[tone="info"] {
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #dbeafe;
}

QLabel#Banner[tone="success"] {
    background: #f0fdf4;
    color: #15803d;
    border: 1px solid #bbf7d0;
}

QLabel#Banner[tone="warning"] {
    background: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
}

QLabel#Banner[tone="danger"] {
    background: #fef2f2;
    color: #be123c;
    border: 1px solid #fecaca;
}

/* 按钮样式 */
QPushButton {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 600;
    color: #334155;
    text-align: center;
}

QPushButton:hover {
    background: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a;
}

QPushButton:pressed {
    background: #f1f5f9;
    border-color: #94a3b8;
}

QPushButton:disabled {
    color: #cbd5e1;
    border-color: #f1f5f9;
    background: #f8fafc;
}

QPushButton#PrimaryButton {
    background: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 10px;
}

QPushButton#PrimaryButton:hover {
    background: #2563eb;
}

QPushButton#PrimaryButton:pressed {
    background: #1d4ed8;
}

QPushButton#PrimaryButton:disabled {
    background: #bfdbfe;
    color: #ffffff;
}

QPushButton#DangerButton {
    background: #ffffff;
    border: 1px solid #fecaca;
    color: #be123c;
}

QPushButton#DangerButton:hover {
    background: #fef2f2;
    border-color: #fda4af;
}

QPushButton#IconButton {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: #64748b;
    padding: 4px;
    font-size: 18px;
}
QPushButton#IconButton:hover {
    background: #e2e8f0;
    color: #334155;
}

/* 输入控件 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px 12px;
    selection-background-color: #bfdbfe;
    selection-color: #0f172a;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #3b82f6;
    padding: 10px 12px; /* Fixed padding for focus state */
}

QSpinBox {
    min-height: 52px;
    padding: 0px 32px 0px 12px;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    font-size: 22px;
    font-weight: 700;
    color: #0f172a;
}

QSpinBox:focus {
    border: 2px solid #3b82f6;
    padding: 0px 31px 0px 11px;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 24px;
    background: transparent;
    border: none;
    border-left: 1px solid #e2e8f0;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    border-top-right-radius: 10px;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    border-bottom-right-radius: 10px;
}

QSpinBox::up-arrow {
    image: none;
    width: 0px;
    height: 0px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 6px solid #64748b;
}

QSpinBox::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #f1f5f9;
}

QComboBox {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 8px 12px;
    color: #334155;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #94a3b8;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
    background: transparent;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64748b;
    margin-right: 10px;
}

QComboBox QAbstractItemView {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: #ffffff;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
    outline: none;
    padding: 4px;
}

/* 编辑器特定样式 */
QTextEdit#MarkdownEditor {
    font-family: "Consolas", "Monaco", "Microsoft YaHei Mono", monospace;
    font-size: 15px;
    line-height: 1.6;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    color: #334155;
}

QTextEdit#ReaderContent {
    font-family: "Georgia", "Microsoft YaHei UI", serif;
    font-size: 17px;
    line-height: 1.8;
    background: #ffffff;
    color: #1e293b;
    border: none;
    padding: 30px;
}

QTextEdit#LogViewer {
    font-family: "Consolas", "Monaco", monospace;
    font-size: 13px;
    line-height: 1.5;
    background: #0f172a; /* 深色背景更像终端 */
    color: #f8fafc;
    border: 1px solid #1e293b;
    border-radius: 12px;
}

/* 标签页 */
QTabWidget::pane {
    border: none;
    background: transparent;
}

QTabWidget::tab-bar {
    left: 0;
}

QTabBar::tab {
    background: transparent;
    color: #64748b;
    font-weight: 700;
    padding: 12px 18px;
    margin-right: 8px;
    border-bottom: 3px solid transparent;
    font-size: 15px;
}

QTabBar::tab:hover {
    color: #334155;
    background: #f1f5f9;
    border-radius: 8px;
}

QTabBar::tab:selected {
    color: #2563eb;
    background: #eff6ff;
    border-radius: 8px;
    border-bottom: 3px solid #2563eb;
}

/* 滚动条 */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 40px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* 进度条 */
QProgressBar {
    border: none;
    background: #e2e8f0;
    border-radius: 6px;
    text-align: center;
    color: transparent;
    min-height: 8px;
    max-height: 8px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #6366f1);
    border-radius: 6px;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 24px;
    padding-top: 16px;
    font-weight: 700;
    color: #475569;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 12px;
    color: #64748b;
}

/* Splitter */
QSplitter#MainSplitter::handle:horizontal {
    background: #e2e8f0;
    width: 1px;
}

QSplitter#MainSplitter::handle:horizontal:hover {
    background: #cbd5e1; /* Slightly darker on hover */
}

QSizeGrip {
    width: 14px;
    height: 14px;
    background: transparent;
}
"""
