"""
项目视图模块 (PySide6 版本)

显示项目列表和项目操作按钮。
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QInputDialog,
    QMessageBox, QComboBox,
)
from PySide6.QtCore import Signal, Qt

from src.services.project_service import ProjectService, ProjectInfo
from src.exceptions import ProjectNotFoundError, ProjectAlreadyExistsError


class ProjectView(QWidget):
    """
    项目视图
    
    显示项目列表，支持创建、删除、选择项目。
    
    信号:
        project_selected: 项目被选中 (project_name)
        project_created: 项目创建成功 (project_name)
        project_deleted: 项目删除成功 (project_name)
    """
    
    project_selected = Signal(str)
    project_created = Signal(str)
    project_deleted = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_service = ProjectService()
        self._current_project: Optional[str] = None
        
        self._setup_ui()
        self._load_projects()
    
    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header_layout = QHBoxLayout()
        
        title_label = QLabel("项目列表")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self._style_combo = QComboBox()
        self._style_combo.addItems(["标准模式", "番茄模式"])
        self._style_combo.setToolTip("选择新建项目的文风模式")
        header_layout.addWidget(self._style_combo)
        
        layout.addLayout(header_layout)
        
        self._project_list = QListWidget()
        self._project_list.setMinimumHeight(200)
        self._project_list.itemClicked.connect(self._on_item_clicked)
        self._project_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._project_list)
        
        button_layout = QHBoxLayout()
        
        self._create_btn = QPushButton("新建项目")
        self._create_btn.clicked.connect(self._create_project)
        button_layout.addWidget(self._create_btn)
        
        self._delete_btn = QPushButton("删除项目")
        self._delete_btn.clicked.connect(self._delete_project)
        self._delete_btn.setEnabled(False)
        button_layout.addWidget(self._delete_btn)
        
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.clicked.connect(self._load_projects)
        button_layout.addWidget(self._refresh_btn)
        
        layout.addLayout(button_layout)
        
        self._info_label = QLabel("请选择或创建一个项目")
        self._info_label.setStyleSheet("color: #666; font-size: 12px;")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)
    
    def _load_projects(self):
        """加载项目列表"""
        self._project_list.clear()
        projects = self._project_service.get_all()
        
        for name in projects:
            item = QListWidgetItem(name)
            self._project_list.addItem(item)
        
        self._info_label.setText(f"共 {len(projects)} 个项目")
    
    def _update_project_list(self):
        """更新项目列表"""
        self._load_projects()
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """项目点击"""
        self._delete_btn.setEnabled(True)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """项目双击"""
        self._select_project(item.text())
    
    def _create_project(self):
        """创建项目"""
        name, ok = QInputDialog.getText(
            self,
            "新建项目",
            "请输入项目名称:",
            text="我的小说"
        )
        
        if ok and name.strip():
            style = "tomato" if self._style_combo.currentIndex() == 1 else "standard"
            try:
                self._project_service.create(name.strip(), style)
                self._load_projects()
                self.project_created.emit(name.strip())
                self._select_project(name.strip())
            except ProjectAlreadyExistsError:
                QMessageBox.warning(self, "创建失败", f"项目 '{name}' 已存在")
            except Exception as e:
                QMessageBox.warning(self, "创建失败", str(e))
    
    def _delete_project(self):
        """删除项目"""
        current_item = self._project_list.currentItem()
        if not current_item:
            return
        
        name = current_item.text()
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除项目 '{name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self._project_service.delete(name)
                self._load_projects()
                self.project_deleted.emit(name)
                if self._current_project == name:
                    self._current_project = None
                    self._info_label.setText("请选择或创建一个项目")
            except Exception as e:
                QMessageBox.warning(self, "删除失败", str(e))
    
    def _select_project(self, name: str):
        """选择项目"""
        if self._project_service.exists(name):
            self._current_project = name
            self.project_selected.emit(name)
            
            try:
                info = self._project_service.get_info(name)
                if info:
                    self._info_label.setText(
                        f"当前项目: {name}\n"
                        f"已生成: {info.total_chapters} 章"
                    )
            except Exception:
                self._info_label.setText(f"当前项目: {name}")
    
    def get_current_project(self) -> Optional[str]:
        """获取当前选中的项目"""
        return self._current_project
    
    def get_service(self) -> ProjectService:
        """获取服务"""
        return self._project_service
    
    def refresh(self):
        """刷新"""
        self._load_projects()
