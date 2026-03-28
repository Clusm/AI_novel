import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from gui.styles import Colors, Typography, Spacing, Radius


class WorkspaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择工作区")
        self.setFixedSize(520, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(f"""
            QDialog {{
                background: {Colors.SURFACE};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(int(Spacing.LG.replace("px", "")))
        layout.setContentsMargins(
            int(Spacing.XL.replace("px", "")),
            int(Spacing.XL.replace("px", "")),
            int(Spacing.XL.replace("px", "")),
            int(Spacing.XL.replace("px", ""))
        )
        
        logo = QLabel("✨")
        logo.setStyleSheet(f"""
            font-size: 48px;
            background: transparent;
        """)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        header = QLabel("欢迎使用 AI 写作助手")
        header.setStyleSheet(f"""
            font-size: {Typography.H2["size"]};
            font-weight: {Typography.H2["weight"]};
            color: {Colors.TEXT_PRIMARY};
            background: transparent;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        desc = QLabel("选择一个目录来存储你的小说项目")
        desc.setStyleSheet(f"""
            color: {Colors.TEXT_TERTIARY};
            font-size: {Typography.BODY["size"]};
            background: transparent;
        """)
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(int(Spacing.SM.replace("px", "")))
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("选择或输入目录路径...")
        self.path_input.setClearButtonEnabled(False)
        self.path_input.setMinimumHeight(48)
        self.path_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.SURFACE};
                border: 1px solid {Colors.BORDER};
                border-radius: {Radius.MD};
                padding: 0 {Spacing.MD};
                font-size: {Typography.BODY["size"]};
                color: {Colors.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {Colors.PRIMARY_500};
                padding: 0 15px;
            }}
            QLineEdit::clear-button {{
                width: 0px;
                height: 0px;
                border: none;
                background: transparent;
            }}
        """)
        
        default_path = os.path.join(os.path.expanduser("~"), "Documents", "AI_Novels")
        self.path_input.setText(default_path)
        
        self.btn_browse = QPushButton("浏览")
        self.btn_browse.setMinimumHeight(48)
        self.btn_browse.setMinimumWidth(80)
        self.btn_browse.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.GRAY_100};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: {Radius.MD};
                font-weight: {Typography.WEIGHT_MEDIUM};
                font-size: {Typography.BODY["size"]};
            }}
            QPushButton:hover {{
                background: {Colors.GRAY_200};
                border-color: {Colors.GRAY_300};
            }}
        """)
        self.btn_browse.clicked.connect(self.browse_folder)
        
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(self.btn_browse)
        layout.addLayout(input_layout)
        
        layout.addSpacing(int(Spacing.SM.replace("px", "")))
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        self.btn_ok = QPushButton("开始创作")
        self.btn_ok.setMinimumHeight(48)
        self.btn_ok.setMinimumWidth(140)
        self.btn_ok.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.GRADIENT_PRIMARY};
                color: {Colors.WHITE};
                border: none;
                border-radius: {Radius.MD};
                font-weight: {Typography.WEIGHT_BOLD};
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {Colors.PRIMARY_600};
            }}
            QPushButton:pressed {{
                background: {Colors.PRIMARY_700};
            }}
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
            test_file = os.path.join(path, ".test_write")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            
            self.selected_path = path
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建或写入目录: {str(e)}\n请检查权限或选择其他位置。")
