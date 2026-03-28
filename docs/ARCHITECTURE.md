# AI Novel Writer 架构文档

> 版本: 2.0  
> 更新日期: 2026-03-29  
> 重构后架构说明

---

## 一、系统概述

AI Novel Writer 是一个基于多 Agent 协作的 AI 小说写作系统。系统采用分层架构设计，将 GUI、业务逻辑、数据访问分离，便于维护和扩展。

### 核心特性

- **多 Agent 协作**：基于 CrewAI 框架，4 个专业 Agent 分工协作
- **多模型支持**：支持 DeepSeek、通义千问、Kimi 三种大模型
- **配置驱动**：Agent 和 Task 通过 YAML 配置，无需修改代码
- **服务层抽象**：业务逻辑封装在服务层，便于测试和复用

---

## 二、架构层次

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUI Layer (gui/)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                         Views                                │ │
│  │  ProjectView │ ChapterView │ OutlineView │ MonitorView │ ... │ │
│  └─────────────────────────────┬───────────────────────────────┘ │
│                                │                                 │
│  ┌─────────────────────────────▼───────────────────────────────┐ │
│  │                      Controllers                             │ │
│  │  ProjectController │ ChapterController │ ExportController   │ │
│  └─────────────────────────────┬───────────────────────────────┘ │
└────────────────────────────────┼──────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer (src/services/)                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│  │ProjectService │ │ChapterService │ │ ExportService │          │
│  └───────┬───────┘ └───────┬───────┘ └───────────────┘          │
│          │                 │                                    │
│  ┌───────▼───────┐ ┌───────▼───────┐                           │
│  │  APIService   │ │   (更多...)   │                           │
│  └───────────────┘ └───────────────┘                           │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Business Layer (src/)                         │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│  │ AgentFactory  │ │  TaskBuilder  │ │   Generator   │          │
│  └───────────────┘ └───────────────┘ └───────────────┘          │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│  │    agents     │ │    tasks      │ │    project    │          │
│  └───────────────┘ └───────────────┘ └───────────────┘          │
└────────────────────────────────┬─────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer (src/)                      │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│  │    Config     │ │   Exceptions  │ │     Logger    │          │
│  └───────────────┘ └───────────────┘ └───────────────┘          │
│  ┌───────────────┐ ┌───────────────┐                            │
│  │   Container   │ │   Workspace   │                            │
│  └───────────────┘ └───────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer (文件系统)                        │
│  项目目录/ ├── config.json ├── 大纲.md ├── chapters/             │
│           ├── summaries/ ├── canon/ └── logs/                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、模块说明

### 3.1 基础设施层 (Infrastructure Layer)

#### Config 模块 (`src/config.py`)

统一配置管理，整合所有配置项。

```python
from src.config import AppConfig, get_config

# 获取配置实例
config = get_config()

# 访问配置
print(config.workspace_path)
print(config.route_profile)
print(config.has_api_key("deepseek"))
```

#### Exceptions 模块 (`src/exceptions.py`)

统一异常体系，定义所有业务异常。

```python
from src.exceptions import (
    NovelWriterError,
    APIKeyMissingError,
    ProjectNotFoundError,
    ChapterGenerationError,
)

try:
    # 业务操作
    pass
except NovelWriterError as e:
    print(f"错误: {e}")
    print(f"代码: {e.code}")
```

#### Logger 模块 (`src/logger.py`)

统一日志管理，支持多处理器。

```python
from src.logger import LogManager, log_manager

# 记录日志
log_manager.info("开始生成", module="Generator")
log_manager.success("生成完成", module="Generator")
log_manager.error("生成失败", module="Generator")

# 注册处理器（如 UI 回调）
log_manager.register_handler(my_callback)
```

#### Container 模块 (`src/container.py`)

依赖注入容器，管理服务生命周期。

```python
from src.container import Container

# 注册服务
Container.register("config", lambda: AppConfig.load())

# 获取服务
config = Container.get("config")
```

---

### 3.2 服务层 (Service Layer)

#### ProjectService (`src/services/project_service.py`)

项目管理服务。

```python
from src.services import ProjectService

service = ProjectService()

# 创建项目
service.create("我的小说", style="standard")

# 获取项目列表
projects = service.get_all()

# 获取项目信息
info = service.get_info("我的小说")

# 保存大纲
service.save_outline("我的小说", "# 故事大纲...")
```

#### ChapterService (`src/services/chapter_service.py`)

章节管理服务。

```python
from src.services import ChapterService

service = ChapterService("我的小说")

# 生成章节
content = service.generate(1, outline, log_callback=my_callback)

# 获取章节列表
chapters = service.get_all()

# 读取章节
content = service.get("第1章.md")

# 获取摘要
summary = service.get_summary(1)
```

#### ExportService (`src/services/export_service.py`)

导出服务。

```python
from src.services import ExportService

service = ExportService("我的小说")

# 导出为各种格式
service.to_txt()
service.to_word()
service.to_epub()

# 导出所有格式
paths = service.to_all()
```

#### APIService (`src/services/api_service.py`)

API 管理服务。

```python
from src.services import APIService

service = APIService()

# 加载/保存 API Keys
keys = service.load_keys()
service.save_keys({"DEEPSEEK_API_KEY": "sk-xxx"})

# 测试连接
success, message = service.test_connection("deepseek")

# 验证格式
valid, msg = service.validate_key_format("deepseek", "sk-xxx")
```

---

### 3.3 GUI 层 (GUI Layer)

#### 控制器 (Controllers)

控制器负责处理用户交互，调用服务层，发出信号更新视图。

```python
from gui.controllers import ProjectController

controller = ProjectController()

# 连接信号
controller.projects_changed.connect(self.update_list)
controller.project_loaded.connect(self.on_project_loaded)

# 执行操作
controller.load_projects()
controller.create_project("新小说")
```

#### 视图 (Views)

视图负责显示 UI，接收用户输入，响应控制器信号。

```python
from gui.views import ProjectView

view = ProjectView()

# 连接信号
view.project_selected.connect(self.on_project_selected)

# 获取当前项目
project = view.get_current_project()
```

---

### 3.4 Agent/Task 配置化

#### Agent 配置 (`config/agents.yaml`)

```yaml
agents:
  outline:
    role: "大纲动态优化师"
    goal: "把用户提供的大纲细化成当前章节详细提纲"
    backstory: "你是一位资深网文编辑..."
    model_provider: "deepseek"
    max_iter: 3
    temperature: 0.7
```

#### Agent 工厂 (`src/agent_factory.py`)

```python
from src.agent_factory import AgentFactory

# 加载配置
AgentFactory.load_config()

# 创建 Agent
agent = AgentFactory.create_agent("writer", route_profile="speed")

# 创建所有 Agent
agents = AgentFactory.create_agents(route_profile="balanced")
```

#### Task 构建器 (`src/task_builder.py`)

```python
from src.task_builder import TaskBuilder, TaskContext

# 设置上下文
context = TaskContext(
    chapter_number=1,
    outline="故事大纲...",
    min_chars=3500,
    max_chars=5500,
)

# 构建 Task
builder = TaskBuilder(agents)
tasks = builder.build_tasks(context)
```

---

## 四、数据流

### 4.1 章节生成流程

```
用户点击"生成"
    │
    ▼
ChapterController.start_generation()
    │
    ▼
ChapterService.generate()
    │
    ├──► AgentFactory.create_agents()
    │         │
    │         ▼
    │    从 config/agents.yaml 加载配置
    │    创建 Agent 实例
    │
    ├──► TaskBuilder.build_tasks()
    │         │
    │         ▼
    │    从配置加载模板
    │    构建 Task 实例
    │
    ▼
Generator.run_crew()
    │
    ▼
CrewAI 执行 Agent 协作
    │
    ▼
返回生成结果
    │
    ▼
ChapterService 保存章节
    │
    ▼
ChapterController 发出信号
    │
    ▼
View 更新显示
```

---

## 五、扩展指南

### 5.1 添加新的 Agent

1. 编辑 `config/agents.yaml`：

```yaml
agents:
  my_new_agent:
    role: "新角色"
    goal: "目标描述"
    backstory: "背景故事"
    model_provider: "qwen"
    max_iter: 3
    temperature: 0.7
```

2. 添加对应的 Task 模板：

```yaml
prompt_templates:
  my_new_agent_task: |
    任务描述模板...
```

3. 在 `TaskBuilder` 中添加构建方法。

### 5.2 添加新的导出格式

1. 在 `src/export.py` 中添加导出函数。

2. 在 `ExportService` 中添加对应方法。

3. 在 `ExportView` 中添加 UI 按钮。

### 5.3 添加新的服务

1. 在 `src/services/` 创建新服务类。

2. 在 `src/services/__init__.py` 导出。

3. 在 `Container` 中注册（可选）。

---

## 六、测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_config.py

# 运行特定测试类
pytest tests/test_config.py::TestAppConfig

# 显示详细输出
pytest tests/ -v
```

### 测试覆盖

- `test_config.py`: 配置模块测试
- `test_exceptions.py`: 异常模块测试
- `test_services.py`: 服务层测试

---

## 七、文件结构

```
AI_novel/
├── config/
│   └── agents.yaml           # Agent 配置文件
├── docs/
│   ├── ARCHITECTURE.md       # 架构文档（本文件）
│   └── REFACTOR_PLAN.md      # 重构计划
├── gui/
│   ├── controllers/          # 控制器层
│   │   ├── __init__.py
│   │   ├── base_controller.py
│   │   ├── project_controller.py
│   │   ├── chapter_controller.py
│   │   └── export_controller.py
│   ├── views/                # 视图层
│   │   ├── __init__.py
│   │   ├── project_view.py
│   │   ├── chapter_view.py
│   │   ├── outline_view.py
│   │   ├── monitor_view.py
│   │   └── export_view.py
│   ├── main_window.py        # 主窗口
│   ├── dialogs.py            # 对话框
│   └── workers.py            # 后台工作线程
├── src/
│   ├── services/             # 服务层
│   │   ├── __init__.py
│   │   ├── project_service.py
│   │   ├── chapter_service.py
│   │   ├── export_service.py
│   │   └── api_service.py
│   ├── config.py             # 配置管理
│   ├── exceptions.py         # 异常定义
│   ├── logger.py             # 日志管理
│   ├── container.py          # 依赖注入
│   ├── agent_factory.py      # Agent 工厂
│   ├── task_builder.py       # Task 构建器
│   ├── agents.py             # Agent 定义（旧）
│   ├── tasks.py              # Task 定义（旧）
│   ├── generator.py          # 生成器
│   ├── project.py            # 项目管理
│   ├── api.py                # API 管理
│   ├── export.py             # 导出功能
│   ├── license.py            # 授权管理
│   └── workspace.py          # 工作空间
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest 配置
│   ├── test_config.py        # 配置测试
│   ├── test_exceptions.py    # 异常测试
│   └── test_services.py      # 服务测试
├── main_gui.py               # GUI 入口
├── run_app.py                # 应用启动
└── pyproject.toml            # 项目配置
```

---

## 八、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | - | 初始版本 |
| 2.0 | 2026-03-29 | 重构：分层架构、服务层、配置驱动 |

---

## 九、联系与贡献

如有问题或建议，请提交 Issue 或 Pull Request。
