"""
导出视图模块 (PySide6 版本)

提供导出功能的界面。
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QGroupBox,
)
from PySide6.QtCore import Signal, Qt

from src.services.export_service import ExportService


class ExportView(QWidget):
    """
    导出视图
    
    提供导出为各种格式的功能。
    
    信号:
        export_completed: 导出完成 (path, format)
    """
    
    export_completed = Signal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_project: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        title_label = QLabel("导出发布")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        format_group = QGroupBox("选择导出格式")
        format_layout = QVBoxLayout(format_group)
        
        txt_layout = QHBoxLayout()
        txt_label = QLabel("纯文本格式 (TXT)")
        txt_label.setMinimumWidth(150)
        txt_layout.addWidget(txt_label)
        
        self._txt_btn = QPushButton("导出 TXT")
        self._txt_btn.clicked.connect(self._export_txt)
        txt_layout.addWidget(self._txt_btn)
        
        txt_layout.addStretch()
        format_layout.addLayout(txt_layout)
        
        word_layout = QHBoxLayout()
        word_label = QLabel("Word 文档 (DOCX)")
        word_label.setMinimumWidth(150)
        word_layout.addWidget(word_label)
        
        self._word_btn = QPushButton("导出 Word")
        self._word_btn.clicked.connect(self._export_word)
        word_layout.addWidget(self._word_btn)
        
        word_layout.addStretch()
        format_layout.addLayout(word_layout)
        
        epub_layout = QHBoxLayout()
        epub_label = QLabel("电子书格式 (EPUB)")
        epub_label.setMinimumWidth(150)
        epub_layout.addWidget(epub_label)
        
        self._epub_btn = QPushButton("导出 EPUB")
        self._epub_btn.clicked.connect(self._export_epub)
        epub_layout.addWidget(self._epub_btn)
        
        epub_layout.addStretch()
        format_layout.addLayout(epub_layout)
        
        layout.addWidget(format_group)
        
        all_layout = QHBoxLayout()
        all_layout.addStretch()
        
        self._all_btn = QPushButton("导出所有格式")
        self._all_btn.clicked.connect(self._export_all)
        self._all_btn.setStyleSheet("padding: 10px 20px;")
        all_layout.addWidget(self._all_btn)
        
        all_layout.addStretch()
        layout.addLayout(all_layout)
        
        self._status_label = QLabel("请先选择项目")
        self._status_label.setStyleSheet("color: #666;")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)
        
        layout.addStretch()
    
    def set_project(self, project_name: str):
        """设置当前项目"""
        self._current_project = project_name
        self._status_label.setText(f"当前项目: {project_name}")
    
    def _export_txt(self):
        """导出 TXT"""
        if not self._current_project:
            QMessageBox.warning(self, "导出失败", "请先选择项目")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 TXT 文件",
            self._get_default_path("txt"),
            "文本文件 (*.txt)"
        )
        
        if output_path:
            self._do_export("txt", output_path)
    
    def _export_word(self):
        """导出 Word"""
        if not self._current_project:
            QMessageBox.warning(self, "导出失败", "请先选择项目")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 Word 文件",
            self._get_default_path("word"),
            "Word 文档 (*.docx)"
        )
        
        if output_path:
            self._do_export("word", output_path)
    
    def _export_epub(self):
        """导出 EPUB"""
        if not self._current_project:
            QMessageBox.warning(self, "导出失败", "请先选择项目")
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 EPUB 文件",
            self._get_default_path("epub"),
            "电子书 (*.epub)"
        )
        
        if output_path:
            self._do_export("epub", output_path)
    
    def _export_all(self):
        """导出所有格式"""
        if not self._current_project:
            QMessageBox.warning(self, "导出失败", "请先选择项目")
            return
        
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出目录",
            ""
        )
        
        if output_dir:
            results = self._do_export_all(output_dir)
            
            if results:
                message = "导出完成:\n" + "\n".join(
                    f"  {fmt.upper()}: {path}"
                    for fmt, path in results.items()
                )
                QMessageBox.information(self, "导出完成", message)
            else:
                QMessageBox.warning(self, "导出失败", "所有格式导出失败")
    
    def _do_export(self, format: str, output_path: str):
        """执行导出"""
        service = ExportService(self._current_project)
        
        self._status_label.setText(f"正在导出 {format.upper()}...")
        self._status_label.setStyleSheet("color: #1976D2;")
        self._set_buttons_enabled(False)
        
        try:
            path = service.export(format, output_path)
            self._status_label.setText(f"导出成功: {path}")
            self._status_label.setStyleSheet("color: #4CAF50;")
            self.export_completed.emit(path, format)
        except Exception as e:
            self._status_label.setText(f"导出失败: {e}")
            self._status_label.setStyleSheet("color: #F44336;")
            QMessageBox.warning(self, "导出失败", str(e))
        finally:
            self._set_buttons_enabled(True)
    
    def _do_export_all(self, output_dir: str) -> dict:
        """导出所有格式"""
        service = ExportService(self._current_project)
        
        self._status_label.setText("正在导出所有格式...")
        self._status_label.setStyleSheet("color: #1976D2;")
        self._set_buttons_enabled(False)
        
        try:
            results = service.to_all(output_dir)
            self._status_label.setText("导出完成")
            self._status_label.setStyleSheet("color: #4CAF50;")
            return results
        except Exception as e:
            self._status_label.setText(f"导出失败: {e}")
            self._status_label.setStyleSheet("color: #F44336;")
            return {}
        finally:
            self._set_buttons_enabled(True)
    
    def _get_default_path(self, format: str) -> str:
        """获取默认输出路径"""
        from datetime import datetime
        
        date_str = datetime.now().strftime("%Y%m%d")
        extensions = {"txt": ".txt", "word": ".docx", "epub": ".epub"}
        ext = extensions.get(format, ".txt")
        return f"{self._current_project}_{date_str}{ext}"
    
    def _set_buttons_enabled(self, enabled: bool):
        """设置按钮启用状态"""
        self._txt_btn.setEnabled(enabled)
        self._word_btn.setEnabled(enabled)
        self._epub_btn.setEnabled(enabled)
        self._all_btn.setEnabled(enabled)
    
    def clear(self):
        """清空"""
        self._current_project = None
        self._status_label.setText("请先选择项目")
        self._status_label.setStyleSheet("color: #666;")
