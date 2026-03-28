"""
监控视图模块 (PySide6 版本)

显示运行日志和生成进度。
"""

from typing import List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextBrowser, QProgressBar,
)
from PySide6.QtCore import Signal, Qt

from src.logger import get_logs_html, clear_run_logs


class MonitorView(QWidget):
    """
    监控视图
    
    显示运行日志和生成进度。
    
    信号:
        clear_requested: 请求清空日志
    """
    
    clear_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._logs: List[str] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("运行监控")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self._status_label = QLabel("就绪")
        self._status_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self._status_label)
        
        layout.addLayout(header_layout)
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimum(0)
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("%p%")
        layout.addWidget(self._progress_bar)
        
        self._log_browser = QTextBrowser()
        self._log_browser.setOpenExternalLinks(False)
        self._log_browser.setPlaceholderText("运行日志将显示在这里...")
        layout.addWidget(self._log_browser)
        
        button_layout = QHBoxLayout()
        
        self._clear_btn = QPushButton("清空日志")
        self._clear_btn.clicked.connect(self._clear_logs)
        button_layout.addWidget(self._clear_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self._update_log_display()
    
    def add_log(self, message: str, status: str = "info"):
        """添加日志"""
        from src.logger import add_run_log
        self._logs = add_run_log(self._logs, "系统", message, status)
        self._update_log_display()
    
    def add_log_with_title(self, title: str, message: str, status: str = "info"):
        """添加带标题的日志"""
        from src.logger import add_run_log
        self._logs = add_run_log(self._logs, title, message, status)
        self._update_log_display()
    
    def clear_logs(self):
        """清空日志"""
        self._logs = clear_run_logs(self._logs)
        self._update_log_display()
    
    def _clear_logs(self):
        """清空日志按钮"""
        self.clear_logs()
        self.clear_requested.emit()
    
    def _update_log_display(self):
        """更新日志显示"""
        html = get_logs_html(self._logs)
        self._log_browser.setHtml(html)
        
        scrollbar = self._log_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def set_progress(self, value: int, max_value: int = 100):
        """设置进度"""
        self._progress_bar.setMaximum(max_value)
        self._progress_bar.setValue(value)
    
    def set_status(self, status: str):
        """设置状态"""
        self._status_label.setText(status)
    
    def start_generation(self):
        """开始生成"""
        self._progress_bar.setValue(0)
        self._status_label.setText("生成中...")
        self._status_label.setStyleSheet("color: #1976D2; font-weight: bold;")
    
    def finish_generation(self, success: bool = True):
        """完成生成"""
        self._progress_bar.setValue(100 if success else 0)
        self._status_label.setText("完成" if success else "失败")
        self._status_label.setStyleSheet(
            "color: #4CAF50; font-weight: bold;" if success
            else "color: #F44336; font-weight: bold;"
        )
    
    def get_logs(self) -> List[str]:
        """获取日志列表"""
        return self._logs
