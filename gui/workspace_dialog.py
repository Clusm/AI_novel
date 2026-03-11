import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class WorkspaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择工作区 - AI 写作助手")
        self.setFixedSize(500, 250)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("👋 欢迎使用 AI 写作助手")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        layout.addWidget(header)
        
        desc = QLabel("请选择用于存储所有小说项目的工作目录。")
        desc.setStyleSheet("color: #64748b; font-size: 14px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Input Area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("例如: D:\\MyNovels")
        self.path_input.setMinimumHeight(40)
        
        # Default to Documents folder if empty
        default_path = os.path.join(os.path.expanduser("~"), "Documents", "AI_Novels")
        self.path_input.setText(default_path)
        
        self.btn_browse = QPushButton("浏览...")
        self.btn_browse.setMinimumHeight(40)
        self.btn_browse.clicked.connect(self.browse_folder)
        
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(self.btn_browse)
        layout.addLayout(input_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        self.btn_ok = QPushButton("开始创作")
        self.btn_ok.setMinimumHeight(40)
        self.btn_ok.setMinimumWidth(120)
        self.btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        self.btn_ok.clicked.connect(self.accept_workspace)
        
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择工作目录")
        if folder:
            self.path_input.setText(folder)
            
    def accept_workspace(self):
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "提示", "请选择一个有效的目录")
            return
            
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            # Test write permission
            test_file = os.path.join(path, ".test_write")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            self.selected_path = path
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建或写入目录: {str(e)}\n请检查权限或选择其他位置。")

