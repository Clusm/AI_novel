"""
项目服务模块

封装项目相关的业务逻辑：
1. 项目 CRUD 操作
2. 项目配置管理
3. 项目信息查询
4. 大纲管理
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from src.project import (
    create_new_project,
    delete_project,
    get_all_projects,
    get_project_info,
    load_project_config,
    save_project_config,
    load_outline,
    save_outline,
    list_generated_chapters,
    load_story_bible,
    save_story_bible,
)
from src.exceptions import (
    ProjectNotFoundError,
    ProjectAlreadyExistsError,
    ProjectCreationError,
    ProjectDeletionError,
    OutlineNotFoundError,
    OutlineTooShortError,
)


@dataclass
class ProjectInfo:
    """项目信息数据类"""
    name: str
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    total_chapters: int = 0
    total_planned_chapters: int = 0
    generated_chapters: List[str] = None
    writing_style: str = "standard"
    
    def __post_init__(self):
        if self.generated_chapters is None:
            self.generated_chapters = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectInfo":
        """从字典创建"""
        return cls(
            name=data.get("name", ""),
            created_at=data.get("created_at"),
            last_modified=data.get("last_modified"),
            total_chapters=data.get("total_chapters", 0),
            total_planned_chapters=data.get("total_planned_chapters", 0),
            generated_chapters=data.get("generated_chapters", []),
            writing_style=data.get("writing_style", "standard"),
        )


class ProjectService:
    """
    项目服务
    
    封装项目的所有操作，提供统一的业务接口。
    
    使用示例:
        service = ProjectService()
        
        # 创建项目
        project_name = service.create("我的小说", style="tomato")
        
        # 获取项目列表
        projects = service.get_all()
        
        # 获取项目信息
        info = service.get_info("我的小说")
        
        # 保存大纲
        service.save_outline("我的小说", "# 故事大纲...")
    """
    
    def __init__(self):
        pass
    
    def create(self, name: str, style: str = "standard") -> str:
        """
        创建新项目
        
        参数:
            name: 项目名称
            style: 文风模式（standard/tomato）
        
        返回:
            创建的项目名称
        
        异常:
            ProjectAlreadyExistsError: 项目已存在
            ProjectCreationError: 创建失败
        """
        if not name or not name.strip():
            raise ProjectCreationError("", "项目名称不能为空")
        
        name = name.strip()
        
        existing_projects = get_all_projects()
        if name in existing_projects:
            raise ProjectAlreadyExistsError(name)
        
        try:
            created_name = create_new_project(name, style)
            return created_name
        except Exception as e:
            raise ProjectCreationError(name, str(e)) from e
    
    def delete(self, name: str) -> None:
        """
        删除项目
        
        参数:
            name: 项目名称
        
        异常:
            ProjectNotFoundError: 项目不存在
            ProjectDeletionError: 删除失败
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        try:
            delete_project(name)
        except Exception as e:
            raise ProjectDeletionError(name, str(e)) from e
    
    def get_all(self) -> List[str]:
        """
        获取所有项目名称
        
        返回:
            项目名称列表（按名称排序）
        """
        return get_all_projects()
    
    def exists(self, name: str) -> bool:
        """
        检查项目是否存在
        
        参数:
            name: 项目名称
        
        返回:
            是否存在
        """
        return name in get_all_projects()
    
    def get_info(self, name: str) -> ProjectInfo:
        """
        获取项目信息
        
        参数:
            name: 项目名称
        
        返回:
            项目信息
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        info_dict = get_project_info(name)
        return ProjectInfo.from_dict(info_dict)
    
    def get_config(self, name: str) -> Dict[str, Any]:
        """
        获取项目配置
        
        参数:
            name: 项目名称
        
        返回:
            配置字典
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        return load_project_config(name)
    
    def save_config(self, name: str, config: Dict[str, Any]) -> None:
        """
        保存项目配置
        
        参数:
            name: 项目名称
            config: 配置字典
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        save_project_config(name, config)
    
    def get_outline(self, name: str) -> str:
        """
        获取项目大纲
        
        参数:
            name: 项目名称
        
        返回:
            大纲内容
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        return load_outline(name)
    
    def save_outline(self, name: str, outline: str) -> None:
        """
        保存项目大纲
        
        参数:
            name: 项目名称
            outline: 大纲内容
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        save_outline(name, outline)
    
    def get_story_bible(self, name: str) -> str:
        """
        获取剧情圣经
        
        参数:
            name: 项目名称
        
        返回:
            剧情圣经内容
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        return load_story_bible(name)
    
    def save_story_bible(self, name: str, content: str) -> None:
        """
        保存剧情圣经
        
        参数:
            name: 项目名称
            content: 剧情圣经内容
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        save_story_bible(name, content)
    
    def get_chapters(self, name: str) -> List[str]:
        """
        获取已生成的章节列表
        
        参数:
            name: 项目名称
        
        返回:
            章节文件名列表
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if not self.exists(name):
            raise ProjectNotFoundError(name)
        
        return list_generated_chapters(name)
    
    def get_writing_style(self, name: str) -> str:
        """
        获取项目文风模式
        
        参数:
            name: 项目名称
        
        返回:
            文风模式（standard/tomato）
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        config = self.get_config(name)
        return config.get("writing_style", "standard")
    
    def set_writing_style(self, name: str, style: str) -> None:
        """
        设置项目文风模式
        
        参数:
            name: 项目名称
            style: 文风模式（standard/tomato）
        
        异常:
            ProjectNotFoundError: 项目不存在
        """
        if style not in ("standard", "tomato"):
            style = "standard"
        
        config = self.get_config(name)
        config["writing_style"] = style
        self.save_config(name, config)
    
    def validate_outline(self, outline: str, min_length: int = 50) -> bool:
        """
        验证大纲是否有效
        
        参数:
            outline: 大纲内容
            min_length: 最小长度
        
        返回:
            是否有效
        
        异常:
            OutlineTooShortError: 大纲过短
        """
        if not outline or len(outline.strip()) < min_length:
            raise OutlineTooShortError("", len(outline or ""), min_length)
        
        return True
