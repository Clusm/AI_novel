# AI Novel Writer 重构计划

> 版本: 1.0  
> 创建日期: 2026-03-29  
> 目标: 优化项目架构，为后续功能扩展打下坚实基础

---

## 一、重构目标

### 1.1 核心目标
- **降低耦合度**: GUI 层与业务层解耦，便于独立测试和维护
- **提高可扩展性**: 支持插件化扩展新的 Agent、导出格式、模型
- **统一管理**: 配置、日志、异常统一管理
- **代码可读性**: 拆分大文件，职责单一化

### 1.2 预期收益
| 方面 | 现状 | 重构后 |
|------|------|--------|
| MainWindow 行数 | 2400+ 行 | < 300 行（容器） |
| 配置管理 | 分散在 5+ 个模块 | 统一 AppConfig 类 |
| 测试覆盖 | 难以单元测试 | 服务层可独立测试 |
| 新增 Agent | 修改源码 | YAML 配置即可 |

---

## 二、重构阶段规划

```
Phase 1: 基础设施层 (优先级: 高)
    ↓
Phase 2: 服务层抽象 (优先级: 高)
    ↓
Phase 3: GUI 层重构 (优先级: 中)
    ↓
Phase 4: Agent/Task 配置化 (优先级: 低)
    ↓
Phase 5: 测试与文档 (优先级: 低)
```

---

## 三、详细任务清单

### Phase 1: 基础设施层

#### 任务 1.1: 统一配置管理
**文件**: `src/config.py` (新建)

**内容**:
```python
@dataclass
class AppConfig:
    # 路径配置
    workspace_path: str
    config_dir: str
    
    # API 配置
    deepseek_api_key: str
    dashscope_api_key: str
    moonshot_api_key: str
    
    # 模型配置
    route_profile: str  # speed/balanced/quality
    writer_model: str   # auto/qwen/kimi
    model_preset: str   # default/custom
    
    # 生成配置
    chapter_min_chars: int
    chapter_max_chars: int
    kickoff_timeout: int
    
    # 功能开关
    enable_memory: bool
    enable_dedup: bool
```

**影响文件**:
- `src/api.py` - 移除配置相关代码
- `src/workspace.py` - 使用 AppConfig
- `src/generator.py` - 使用 AppConfig
- `main_gui.py` - 使用 AppConfig

**验收标准**:
- [ ] 所有配置通过 AppConfig 读取
- [ ] 配置变更自动保存
- [ ] 支持配置热重载

---

#### 任务 1.2: 统一异常体系
**文件**: `src/exceptions.py` (新建)

**内容**:
```python
class NovelWriterError(Exception): pass
class APIKeyMissingError(NovelWriterError): pass
class GenerationFailedError(NovelWriterError): pass
class ProjectNotFoundError(NovelWriterError): pass
class LicenseInvalidError(NovelWriterError): pass
class ExportFailedError(NovelWriterError): pass
```

**影响文件**:
- `src/generator.py` - 使用自定义异常
- `src/api.py` - 使用自定义异常
- `src/project.py` - 使用自定义异常
- `src/license.py` - 使用自定义异常
- `src/export.py` - 使用自定义异常

**验收标准**:
- [ ] 所有业务异常使用自定义类
- [ ] 异常信息用户友好
- [ ] GUI 层统一捕获处理

---

#### 任务 1.3: 统一日志管理
**文件**: `src/logger.py` (增强)

**新增内容**:
```python
class LogManager:
    def register_handler(self, handler: Callable)
    def info(self, message: str, module: str)
    def error(self, message: str, module: str)
    def warning(self, message: str, module: str)
    def success(self, message: str, module: str)

# 全局实例
log = LogManager()
```

**影响文件**:
- `src/generator.py` - 使用 LogManager
- `gui/workers.py` - 使用 LogManager
- `gui/main_window.py` - 注册 UI 日志处理器

**验收标准**:
- [ ] 所有日志通过 LogManager
- [ ] 支持多处理器（文件、UI、控制台）
- [ ] 日志格式统一

---

#### 任务 1.4: 依赖注入容器
**文件**: `src/container.py` (新建)

**内容**:
```python
class Container:
    @classmethod
    def register(cls, name: str, factory: Callable)
    
    @classmethod
    def get(cls, name: str) -> T
    
    @classmethod
    def reset(cls)

# 注册核心服务
Container.register("config", lambda: AppConfig.load())
Container.register("log", lambda: LogManager())
Container.register("workspace", lambda: WorkspaceManager())
```

**验收标准**:
- [ ] 核心服务通过容器获取
- [ ] 支持测试时替换实现

---

### Phase 2: 服务层抽象

#### 任务 2.1: 项目服务
**文件**: `src/services/__init__.py`, `src/services/project_service.py` (新建)

**内容**:
```python
class ProjectService:
    def create(self, name: str, style: str) -> str
    def delete(self, name: str) -> None
    def get_all(self) -> List[str]
    def get_info(self, name: str) -> ProjectInfo
    def get_config(self, name: str) -> dict
    def save_config(self, name: str, config: dict) -> None
```

**验收标准**:
- [ ] 项目 CRUD 操作封装
- [ ] 异常统一处理
- [ ] 可独立单元测试

---

#### 任务 2.2: 章节服务
**文件**: `src/services/chapter_service.py` (新建)

**内容**:
```python
class ChapterService:
    def __init__(self, project_name: str)
    
    def generate(self, chapter_number: int, outline: str, 
                 log_callback: Callable = None) -> str
    def generate_batch(self, start: int, count: int, 
                       outline: str, log_callback: Callable = None) -> List[str]
    def get_all(self) -> List[str]
    def get(self, chapter_file: str) -> str
    def get_summary(self, chapter_number: int) -> str
    def get_canon(self, chapter_number: int) -> str
```

**验收标准**:
- [ ] 章节生成逻辑封装
- [ ] 支持进度回调
- [ ] 异常统一处理

---

#### 任务 2.3: 导出服务
**文件**: `src/services/export_service.py` (新建)

**内容**:
```python
class ExportService:
    def __init__(self, project_name: str)
    
    def to_txt(self, output_path: str = None) -> str
    def to_word(self, output_path: str = None) -> str
    def to_epub(self, output_path: str = None) -> str
    def to_all(self, output_dir: str = None) -> dict
```

**验收标准**:
- [ ] 导出逻辑封装
- [ ] 支持自定义输出路径
- [ ] 异常统一处理

---

#### 任务 2.4: API 服务
**文件**: `src/services/api_service.py` (新建)

**内容**:
```python
class APIService:
    def load_keys(self) -> dict
    def save_keys(self, keys: dict) -> None
    def test_connection(self, provider: str) -> Tuple[bool, str]
    def test_all(self) -> dict
```

**验收标准**:
- [ ] API 配置操作封装
- [ ] 连接测试封装

---

### Phase 3: GUI 层重构

#### 任务 3.1: 创建控制器基类
**文件**: `gui/controllers/__init__.py`, `gui/controllers/base_controller.py` (新建)

**内容**:
```python
class BaseController(QObject):
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._services = {}
    
    def register_service(self, name: str, service: Any)
    def get_service(self, name: str) -> Any
```

---

#### 任务 3.2: 项目控制器
**文件**: `gui/controllers/project_controller.py` (新建)

**内容**:
```python
class ProjectController(BaseController):
    projects_changed = Signal()
    project_loaded = Signal(str)
    
    def load_projects(self) -> List[str]
    def create_project(self, name: str, style: str) -> str
    def delete_project(self, name: str) -> None
    def select_project(self, name: str) -> None
```

---

#### 任务 3.3: 章节控制器
**文件**: `gui/controllers/chapter_controller.py` (新建)

**内容**:
```python
class ChapterController(BaseController):
    generation_started = Signal()
    generation_progress = Signal(int, int, str)
    generation_finished = Signal(bool, str)
    chapter_generated = Signal(int)
    
    def start_generation(self, project: str, outline: str, 
                         start: int, count: int) -> None
    def stop_generation(self) -> None
    def load_chapters(self, project: str) -> List[str]
    def load_chapter(self, project: str, chapter: str) -> str
```

---

#### 任务 3.4: 导出控制器
**文件**: `gui/controllers/export_controller.py` (新建)

**内容**:
```python
class ExportController(BaseController):
    export_finished = Signal(str, str)  # path, format
    
    def export_txt(self, project: str) -> str
    def export_word(self, project: str) -> str
    def export_epub(self, project: str) -> str
    def export_all(self, project: str) -> dict
```

---

#### 任务 3.5: 拆分 MainWindow
**文件**: `gui/main_window.py` (重构)

**拆分策略**:
```
main_window.py (精简为容器，< 300 行)
    ├── gui/views/project_view.py      # 项目选择区
    ├── gui/views/chapter_view.py      # 章节阅读区
    ├── gui/views/outline_view.py      # 大纲编辑区
    ├── gui/views/monitor_view.py      # 运行监控区
    ├── gui/views/export_view.py       # 导出发布区
    └── gui/views/dashboard_view.py    # 仪表盘统计
```

**重构后 MainWindow 职责**:
- 创建和布局各个视图
- 初始化控制器
- 连接信号和槽
- 处理窗口级事件（关闭、拖拽、缩放）

**验收标准**:
- [ ] MainWindow 行数 < 300
- [ ] 各视图独立可测试
- [ ] 功能与重构前一致

---

### Phase 4: Agent/Task 配置化

#### 任务 4.1: Agent 配置文件
**文件**: `config/agents.yaml` (新建)

**内容**:
```yaml
agents:
  outline:
    role: "大纲动态优化师"
    goal: "把用户提供的大纲细化成当前章节详细提纲"
    backstory: "你是一位资深网文编辑..."
    model_provider: "deepseek"
    max_iter: 3
    max_execution_time: 600
    
  character:
    role: "人物与世界观守护者"
    goal: "维护完整人物卡、世界观一致性检查"
    model_provider: "qwen"
    max_iter: 3
    max_execution_time: 300
    
  writer:
    role: "章节主写手"
    goal: "根据最新大纲+人物卡写出符合字数要求的正文"
    model_provider: "qwen"
    max_iter: 5
    max_execution_time: 900
    
  finalizer:
    role: "终极审校专家"
    goal: "润色正文、检查一致性"
    model_provider: "kimi"
    max_iter: 3
    max_execution_time: 600
```

---

#### 任务 4.2: Agent 工厂
**文件**: `src/agent_factory.py` (新建)

**内容**:
```python
class AgentFactory:
    @classmethod
    def load_config(cls) -> dict
    
    @classmethod
    def create_agents(cls, runtime_config: dict = None) -> List[Agent]
    
    @classmethod
    def create_single(cls, role: str, config: dict = None) -> Agent
```

---

#### 任务 4.3: Task 构建器
**文件**: `src/task_builder.py` (新建)

**内容**:
```python
class TaskBuilder:
    def __init__(self, agents: List[Agent])
    
    def build_tasks(self, context: TaskContext) -> List[Task]
    
    def build_outline_task(self, context: TaskContext) -> Task
    def build_character_task(self, context: TaskContext) -> Task
    def build_writer_task(self, context: TaskContext) -> Task
    def build_finalizer_task(self, context: TaskContext) -> Task
```

---

### Phase 5: 测试与文档

#### 任务 5.1: 单元测试
**目录**: `tests/` (新建)

```
tests/
├── __init__.py
├── conftest.py              # pytest 配置和 fixtures
├── test_config.py           # 配置管理测试
├── test_exceptions.py       # 异常测试
├── test_services/
│   ├── test_project_service.py
│   ├── test_chapter_service.py
│   └── test_export_service.py
├── test_controllers/
│   ├── test_project_controller.py
│   └── test_chapter_controller.py
└── test_integration/
    └── test_generation_flow.py
```

**验收标准**:
- [ ] 核心服务测试覆盖 > 80%
- [ ] 所有测试通过

---

#### 任务 5.2: 更新架构文档
**文件**: `docs/ARCHITECTURE.md` (更新)

**内容**:
- 新架构图
- 各层职责说明
- 模块依赖关系
- 扩展指南

---

## 四、文件变更清单

### 新建文件
| 文件路径 | 说明 |
|----------|------|
| `src/config.py` | 统一配置管理 |
| `src/exceptions.py` | 自定义异常 |
| `src/container.py` | 依赖注入容器 |
| `src/services/__init__.py` | 服务层包 |
| `src/services/project_service.py` | 项目服务 |
| `src/services/chapter_service.py` | 章节服务 |
| `src/services/export_service.py` | 导出服务 |
| `src/services/api_service.py` | API 服务 |
| `gui/controllers/__init__.py` | 控制器包 |
| `gui/controllers/base_controller.py` | 控制器基类 |
| `gui/controllers/project_controller.py` | 项目控制器 |
| `gui/controllers/chapter_controller.py` | 章节控制器 |
| `gui/controllers/export_controller.py` | 导出控制器 |
| `gui/views/__init__.py` | 视图包 |
| `gui/views/project_view.py` | 项目视图 |
| `gui/views/chapter_view.py` | 章节视图 |
| `gui/views/outline_view.py` | 大纲视图 |
| `gui/views/monitor_view.py` | 监控视图 |
| `gui/views/export_view.py` | 导出视图 |
| `config/agents.yaml` | Agent 配置 |
| `src/agent_factory.py` | Agent 工厂 |
| `src/task_builder.py` | Task 构建器 |
| `tests/` | 测试目录 |

### 修改文件
| 文件路径 | 变更说明 |
|----------|----------|
| `src/api.py` | 移除配置管理代码，使用 AppConfig |
| `src/workspace.py` | 使用 AppConfig 和 Container |
| `src/generator.py` | 使用服务层和 LogManager |
| `src/project.py` | 使用自定义异常 |
| `src/export.py` | 使用自定义异常 |
| `src/license.py` | 使用自定义异常 |
| `src/logger.py` | 增强 LogManager |
| `gui/main_window.py` | 拆分为多个视图，使用控制器 |
| `gui/workers.py` | 使用服务层 |
| `main_gui.py` | 使用 Container 初始化 |
| `docs/ARCHITECTURE.md` | 更新架构文档 |

---

## 五、执行顺序

```
Week 1: Phase 1 (基础设施层)
├── Day 1-2: 任务 1.1 统一配置管理
├── Day 3: 任务 1.2 统一异常体系
├── Day 4: 任务 1.3 统一日志管理
└── Day 5: 任务 1.4 依赖注入容器

Week 2: Phase 2 (服务层抽象)
├── Day 1: 任务 2.1 项目服务
├── Day 2: 任务 2.2 章节服务
├── Day 3: 任务 2.3 导出服务
└── Day 4-5: 任务 2.4 API 服务 + 集成测试

Week 3: Phase 3 (GUI 层重构)
├── Day 1: 任务 3.1-3.2 控制器基类和项目控制器
├── Day 2: 任务 3.3 章节控制器
├── Day 3: 任务 3.4 导出控制器
└── Day 4-5: 任务 3.5 拆分 MainWindow

Week 4: Phase 4-5 (配置化 + 测试文档)
├── Day 1-2: 任务 4.1-4.3 Agent/Task 配置化
├── Day 3-4: 任务 5.1 单元测试
└── Day 5: 任务 5.2 更新文档
```

---

## 六、风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 重构过程中功能回归 | 高 | 每个 Phase 后进行完整功能测试 |
| GUI 拆分后信号连接错误 | 中 | 保留原文件备份，逐步迁移 |
| 服务层抽象不完整 | 中 | 先封装核心路径，边缘功能后续迭代 |
| 配置迁移数据丢失 | 高 | 提供配置迁移脚本，保留旧格式兼容 |

---

## 七、验收标准

### Phase 1 完成标准
- [ ] 所有配置通过 AppConfig 管理
- [ ] 自定义异常覆盖所有业务场景
- [ ] LogManager 支持多处理器
- [ ] Container 可获取核心服务

### Phase 2 完成标准
- [ ] 服务层封装所有业务逻辑
- [ ] 服务层可独立单元测试
- [ ] GUI 层通过服务层访问数据

### Phase 3 完成标准
- [ ] MainWindow 行数 < 300
- [ ] 所有视图独立可复用
- [ ] 功能与重构前一致

### Phase 4 完成标准
- [ ] Agent 通过 YAML 配置
- [ ] 新增 Agent 无需修改源码

### Phase 5 完成标准
- [ ] 核心服务测试覆盖 > 80%
- [ ] 架构文档更新完成

---

## 八、回滚方案

每个 Phase 完成后创建 Git 标签：
```bash
git tag -a refactor-phase1-complete -m "Phase 1: 基础设施层完成"
git tag -a refactor-phase2-complete -m "Phase 2: 服务层抽象完成"
git tag -a refactor-phase3-complete -m "Phase 3: GUI层重构完成"
git tag -a refactor-phase4-complete -m "Phase 4: Agent/Task配置化完成"
git tag -a refactor-phase5-complete -m "Phase 5: 测试与文档完成"
```

如遇重大问题，可回滚到上一个标签：
```bash
git checkout refactor-phase{n-1}-complete
```

---

**确认此计划后，将开始执行 Phase 1 的任务。**
