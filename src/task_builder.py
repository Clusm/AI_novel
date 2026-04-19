"""
Task 构建器模块

提供配置驱动的 Task 创建：
1. 从模板构建 Task
2. 支持上下文传递
3. 支持自定义 Task
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class TaskContext:
    """Task 上下文数据"""
    chapter_number: int = 1
    outline: str = ""
    previous_summary: str = ""
    character_info: str = ""
    chapter_content: str = ""
    existing_characters: str = ""
    chapter_outline: str = ""
    character_cards: str = ""
    min_chars: int = 3500
    max_chars: int = 5500
    writing_style: str = "standard"


class TaskBuilder:
    """
    Task 构建器
    
    从配置和上下文创建 Task 实例。
    
    使用示例:
        builder = TaskBuilder(agents)
        
        # 设置上下文
        context = TaskContext(
            chapter_number=1,
            outline="故事大纲...",
            min_chars=3500,
            max_chars=5500,
        )
        
        # 构建所有 Task
        tasks = builder.build_tasks(context)
        
        # 构建单个 Task
        outline_task = builder.build_outline_task(context)
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        初始化 Task 构建器
        
        参数:
            agents: Agent 实例字典 {role: agent}
        """
        self._agents = agents
    
    def build_tasks(self, context: TaskContext) -> List[Any]:
        """
        构建所有 Task
        
        参数:
            context: Task 上下文
        
        返回:
            Task 实例列表
        """
        tasks = []
        
        outline_task = self.build_outline_task(context)
        if outline_task:
            tasks.append(outline_task)
        
        character_task = self.build_character_task(context, tasks)
        if character_task:
            tasks.append(character_task)
        
        writer_task = self.build_writer_task(context, tasks)
        if writer_task:
            tasks.append(writer_task)
        
        finalizer_task = self.build_finalizer_task(context, tasks)
        if finalizer_task:
            tasks.append(finalizer_task)
        
        return tasks
    
    def build_outline_task(self, context: TaskContext) -> Any:
        """
        构建大纲优化 Task
        
        参数:
            context: Task 上下文
        
        返回:
            Task 实例
        """
        from crewai import Task
        from src.agent_factory import AgentFactory
        
        agent = self._agents.get("outline")
        if not agent:
            return None
        
        template = AgentFactory.get_prompt_template("outline_task")
        
        description = template.format(
            chapter_number=context.chapter_number,
            outline=context.outline,
            previous_summary=context.previous_summary or "这是第一章，没有前情提要",
            character_info=context.character_info or "暂无人物信息",
        )
        
        return Task(
            description=description,
            expected_output="本章详细提纲、爽点清单、伏笔安排",
            agent=agent,
        )
    
    def build_character_task(
        self,
        context: TaskContext,
        previous_tasks: List[Any],
    ) -> Any:
        """
        构建人物守护 Task
        
        参数:
            context: Task 上下文
            previous_tasks: 前置 Task 列表
        
        返回:
            Task 实例
        """
        from crewai import Task
        from src.agent_factory import AgentFactory
        
        agent = self._agents.get("character")
        if not agent:
            return None
        
        template = AgentFactory.get_prompt_template("character_task")
        
        description = template.format(
            chapter_content=context.chapter_content or "待生成",
            existing_characters=context.existing_characters or "暂无人物卡",
        )
        
        return Task(
            description=description,
            expected_output="更新后的人物卡",
            agent=agent,
            context=previous_tasks if previous_tasks else None,
        )
    
    def build_writer_task(
        self,
        context: TaskContext,
        previous_tasks: List[Any],
    ) -> Any:
        """
        构建主写手 Task
        
        参数:
            context: Task 上下文
            previous_tasks: 前置 Task 列表
        
        返回:
            Task 实例
        """
        from crewai import Task
        from src.agent_factory import AgentFactory
        
        agent = self._agents.get("writer")
        if not agent:
            return None
        
        template = AgentFactory.get_prompt_template("writer_task")
        
        style_names = {
            "standard": "标准网文风格",
            "tomato": "番茄小说风格",
        }
        
        description = template.format(
            chapter_number=context.chapter_number,
            chapter_outline=context.chapter_outline or "根据大纲生成",
            character_cards=context.character_cards or "暂无人物卡",
            min_chars=context.min_chars,
            max_chars=context.max_chars,
            writing_style=style_names.get(context.writing_style, "标准网文风格"),
        )
        
        return Task(
            description=description,
            expected_output=f"第{context.chapter_number}章正文，字数{context.min_chars}-{context.max_chars}字",
            agent=agent,
            context=previous_tasks if previous_tasks else None,
        )
    
    def build_finalizer_task(
        self,
        context: TaskContext,
        previous_tasks: List[Any],
    ) -> Any:
        """
        构建审校 Task
        
        参数:
            context: Task 上下文
            previous_tasks: 前置 Task 列表
        
        返回:
            Task 实例
        """
        from crewai import Task
        from src.agent_factory import AgentFactory
        
        agent = self._agents.get("finalizer")
        if not agent:
            return None
        
        template = AgentFactory.get_prompt_template("finalizer_task")
        
        description = template.format(
            chapter_content=context.chapter_content or "待审校内容",
            character_cards=context.character_cards or "暂无人物卡",
        )
        
        return Task(
            description=description,
            expected_output="审校后的正文内容",
            agent=agent,
            context=previous_tasks if previous_tasks else None,
        )
    
    def build_custom_task(
        self,
        role: str,
        description: str,
        expected_output: str,
        context_tasks: Optional[List[Any]] = None,
    ) -> Any:
        """
        构建自定义 Task
        
        参数:
            role: Agent 角色
            description: Task 描述
            expected_output: 期望输出
            context_tasks: 上下文 Task 列表
        
        返回:
            Task 实例
        """
        from crewai import Task
        
        agent = self._agents.get(role)
        if not agent:
            raise ValueError(f"未找到 Agent: {role}")
        
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            context=context_tasks,
        )


def create_chapter_generation_crew(
    project_name: str,
    chapter_number: int,
    outline: str,
    route_profile: str = "speed",
    log_callback: Optional[callable] = None,
) -> Any:
    """
    创建章节生成 Crew
    
    这是一个便捷函数，用于快速创建完整的章节生成流程。
    
    参数:
        project_name: 项目名称
        chapter_number: 章节序号
        outline: 故事大纲
        route_profile: 路由策略
        log_callback: 日志回调
    
    返回:
        Crew 实例
    """
    from crewai import Crew, Process
    from src.agent_factory import AgentFactory
    from src.project import (
        load_chapter_summary,
        load_story_bible,
        load_project_config,
    )
    
    agents = AgentFactory.create_agents(route_profile)
    
    config = load_project_config(project_name)
    writing_style = config.get("writing_style", "standard")
    
    min_chars = 3500
    max_chars = 5500
    if writing_style == "tomato":
        min_chars = 2900
        max_chars = 3400
    
    previous_summary = ""
    if chapter_number > 1:
        previous_summary = load_chapter_summary(project_name, chapter_number - 1)
    
    character_info = load_story_bible(project_name)
    
    context = TaskContext(
        chapter_number=chapter_number,
        outline=outline,
        previous_summary=previous_summary,
        character_info=character_info,
        min_chars=min_chars,
        max_chars=max_chars,
        writing_style=writing_style,
    )
    
    builder = TaskBuilder(agents)
    tasks = builder.build_tasks(context)
    
    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    
    return crew
