# 业务逻辑重构大纲：启用 Memory + Agent Tools 协作

> **文档版本**：v2.0（修订）
> **对应项目版本**：AI_Novel_Writer v2.4.0
> **CrewAI 版本**：>= 0.75.0
> **修订说明**：基于对实际代码的深入审阅，纠正了初版中对 CrewAI 机制的若干误解，聚焦真实可落地的改进方向。

---

## 一、现状分析

### 1.1 现有架构概览

```
用户输入大纲
     │
     ▼
generate_chapter()
     │
     ├─► [上下文准备]
     │     ├── 加载上一章摘要（summaries/第N章摘要.md）
     │     ├── 加载上一章正文末尾（chapters/第N章.md 末200字）
     │     ├── 加载最近台账（canon/台账.md，最近5条）
     │     └── 加载/生成剧情圣经（剧情圣经.md）
     │
     ├─► [create_agents()]  → 4个Agent（固定LLM、无Tools）
     │
     ├─► [create_tasks()]   → 3-4个Task（上下文通过description硬编码传入）
     │
     ├─► [Crew.kickoff()]   → Sequential流水线执行
     │     ├── Task1（可选）: 大纲优化师 → 细化大纲
     │     ├── Task2:        人物守护者  → 人物卡+一致性检查表
     │     ├── Task3:        主写手      → 正文 + [SUMMARY_BEGIN]块
     │     └── Task4:        审校专家    → 最终定稿
     │
     └─► [后处理]
           ├── 提取正文 + 摘要块
           ├── 字数检查（不足则 _expand_chapter_to_min_length）
           ├── 开头去重（_dedupe_opening_if_needed）
           ├── 保存章节（chapters/第N章.md）
           ├── 保存台账（canon/台账.md）
           └── 保存摘要（summaries/第N章摘要.md）
```

### 1.2 当前 Crew 初始化参数（实际代码）

```python
# src/generator.py ~870行
crew = Crew(
    agents=agents,
    tasks=tasks,
    process=Process.sequential,
    verbose=False,
    memory=memory_enabled,          # 来自配置，但默认被 api.py 强制关闭
    embedder=embedder if memory_enabled else None,
    step_callback=step_callback,
)
```

```python
# src/api.py 中存在硬编码
os.environ["CREWAI_ENABLE_MEMORY"] = "false"   # ← 强制关闭Memory
```

### 1.3 当前流程的核心问题

| 问题 | 位置 | 影响 |
|------|------|------|
| **Memory 被强制关闭** | `src/api.py` 硬编码 `CREWAI_ENABLE_MEMORY=false` | 跨章节向量记忆完全失效，即使配置了也无效 |
| **embedder 未验证** | `get_embedder_config()` 返回 OpenAI 兼容格式 | CrewAI >= 0.75 的 embedder 格式待确认 |
| **Agent 无 Tools** | `src/agents.py` 未配置任何 Tool | Agent 只能依赖 Task.description 中的预注入文本 |
| **上下文全量硬编码** | `src/tasks.py` 将剧情圣经、台账、摘要全部拼入 description | Token 消耗高，且无法动态检索 |
| **无跨章节检索能力** | 无 Memory → 无向量检索 | 每章都需手动拼入历史信息，易遗漏、无法模糊检索 |

### 1.4 已有机制（不需要重复造轮子）

| 机制 | 实现位置 | 说明 |
|------|---------|------|
| **顺序输出传递** | CrewAI Process.sequential | Task N 的输出**自动**成为 Task N+1 的上下文，无需手动设置 `context` 参数 |
| **剧情圣经** | `ensure_story_bible()` | 从大纲提炼全局设定，避免每章传入完整大纲 |
| **摘要 + 台账** | `_build_chapter_summary()` / `_build_canon_ledger()` | 确定性的历史上下文链路已建立 |
| **超时控制** | `generate_chapter()` 失败后切换 compact_mode | 已有降级策略 |
| **扩写 + 去重** | `_expand_chapter_to_min_length()` / `_dedupe_opening_if_needed()` | 后处理质量保障已完善 |

---

## 二、目标架构

### 2.1 核心改进方向

```
改进前（现状）                改进后（目标）
─────────────────────        ─────────────────────────────────────
Memory 被强制关闭       →    Memory 可配置启用（默认关闭，用户控制）
embedder 格式未验证     →    embedder 格式经 CrewAI 0.75 验证
Agent 无 Tools          →    守护者/写手 配备文件读取 Tools
上下文全量硬编码        →    上下文按优先级裁剪 + Memory 辅助检索
无跨章节检索            →    Memory 存储每章摘要，支持向量检索
```

### 2.2 Memory 的真正价值（澄清误区）

```
┌───────────────────────────────────────────────────────────┐
│  单次章节生成内部（无需 Memory，Sequential 已自动传递）      │
│                                                           │
│  Task1 ──输出──► Task2 ──输出──► Task3 ──输出──► Task4   │
│         ↑CrewAI 自动传递，无需手动配置 context 参数        │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│  跨章节（Memory 的真正用途）                                │
│                                                           │
│  第1章生成 → 写入 Memory（向量化章节摘要、关键事件）         │
│  第2章生成 → 写入 Memory                                   │
│  ...                                                      │
│  第N章生成 → 从 Memory 检索"第1~N-1章中与本章相关的内容"     │
│             → 自动补充到 Agent 的执行上下文                 │
│                                                           │
│  效果：即使第1章的某个细节在台账中未记录，                   │
│        Memory 仍可在第N章被模糊检索到                       │
└───────────────────────────────────────────────────────────┘
```

**关键结论**：Memory 是对现有"摘要+台账"确定性链路的**补充**，不是替代。它处理的是"无结构、跨章节的模糊检索"场景。

### 2.3 改进后的流水线

```
用户输入大纲
     │
     ▼
generate_chapter()
     │
     ├─► [上下文准备（增强）]
     │     ├── 加载上一章摘要
     │     ├── 加载上一章正文末尾
     │     ├── 加载最近台账
     │     ├── 加载/生成剧情圣经
     │     └── ⚡ 若 Memory 已启用：自动注入相关历史记忆（CrewAI 内部处理）
     │
     ├─► [create_agents()（增强）]
     │     ├── Agent1: 大纲优化师   （DeepSeek，无Tools，max_iter=3）
     │     ├── Agent2: 人物守护者   （Qwen，+ 读取人物卡 Tool，max_iter=3）
     │     ├── Agent3: 主写手       （Qwen/Kimi，+ 读取大纲 Tool，max_iter=3）
     │     └── Agent4: 审校专家     （Kimi/Qwen，无Tools，max_iter=2）
     │
     ├─► [create_tasks()（不变）]   → description 中的上下文拼接逻辑保持
     │     注：Sequential 模式下 Task 输出自动传递，无需手动设置 context
     │
     ├─► [Crew.kickoff()（增强）]
     │     ├── memory=True（若已配置 embedder）
     │     ├── embedder=embedder_config（DashScope text-embedding-v3）
     │     └── 执行流水线同现有逻辑
     │
     └─► [后处理（不变）]
           └── 现有后处理逻辑完整保留
```

---

## 三、技术设计

### 3.1 Memory 存储架构

```
projects/<project_name>/
├── .crewai/                      # CrewAI Memory 存储目录（已存在）
│   ├── short_term/               # 短期记忆（当次 Crew 运行内）
│   ├── long_term/                # 长期记忆（跨 Crew 运行，需 embedder）
│   │   └── lancedb/              # CrewAI 0.75 默认使用 LanceDB
│   └── entities/                 # 实体记忆（人物/地点等）
│
├── chapters/
├── summaries/
├── canon/
└── 剧情圣经.md
```

> **注意**：CrewAI >= 0.75 已从 ChromaDB 迁移到 **LanceDB** 作为默认向量存储。
> 依赖中已有 `pysqlite3-binary`（Windows 修复），LanceDB 需确认是否需要额外安装。

**清理策略**：
- 保留最近 20 章的 Memory 内容（按章节号 tag 过滤）
- 超出后仅保留章节摘要级别的内容（压缩旧记忆）
- 提供 GUI 按钮手动清理 Memory

### 3.2 embedder 配置（待验证格式）

```python
# CrewAI >= 0.75 的 embedder 配置格式
# 当前代码中 get_embedder_config() 返回的是 OpenAI 兼容格式
# 需要验证此格式在 CrewAI 0.75+ 中是否仍然有效

EMBEDDER_CONFIG = {
    "provider": "openai",
    "config": {
        "api_key": os.environ.get("DASHSCOPE_API_KEY", ""),
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "text-embedding-v3",
    },
}
```

**验证清单（Phase 1 必须完成）**：
- [ ] 在 CrewAI 0.75 源码中确认 `embedder` 参数接受的格式
- [ ] 验证 DashScope `text-embedding-v3` 在 OpenAI 兼容格式下的实际可用性
- [ ] 确认 LanceDB 在 Windows 上的安装与路径兼容性

**备选方案（若 DashScope embedding 不兼容）**：
- 使用 `provider: "huggingface"` + 本地模型（离线，无 API 成本）
- 暂时禁用长期 Memory，只启用短期 Memory（无需 embedder）

### 3.3 Agent Tools 设计

Tools 的价值：让 Agent 在运行时**按需读取**文件，而非在 Task.description 中全量预注入。

| Agent | Tool 名称 | 功能 | 目标文件 |
|-------|-----------|------|---------|
| 人物守护者 | `read_character_cards` | 读取当前项目的人物卡 | `projects/<name>/characters/*.md` |
| 人物守护者 | `read_world_settings` | 读取世界观设定（从剧情圣经中提取） | `projects/<name>/剧情圣经.md` |
| 主写手 | `read_chapter_outline_detail` | 读取当前章节详细大纲 | `projects/<name>/大纲.md`（指定章节） |
| 主写手 | `read_recent_chapters` | 读取最近2章正文（用于风格参考） | `projects/<name>/chapters/` |

**实现方式**：使用 CrewAI 的 `@tool` 装饰器，在 `src/tools.py`（新建）中定义。

**注意事项**：
- Tools 会**增加 Agent 的 LLM 调用次数**（工具调用也消耗 token）
- `max_iter` 需要合理设置，防止 Agent 反复调用工具
- 若 Tool 调用失败，Agent 应能回退到 Task.description 中的预注入信息

### 3.4 allow_delegation 策略（保持禁用）

经过分析，当前流程**不需要启用** `allow_delegation`：

- 每个 Task 职责清晰，Agent 都有足够上下文完成任务
- Sequential 模式中委托会导致额外的 LLM 调用开销
- 委托链路调试复杂，增加不确定性

**结论**：所有 Agent 保持 `allow_delegation=False`，本次重构不涉及此参数。

### 3.5 上下文优先级与 Token 控制

当前 `create_tasks()` 中上下文拼接顺序（保持不变）：

```
Task.description 中的上下文优先级（从高到低）：
1. 本章大纲指引（_extract_outline_excerpt）      ← 最关键，必须包含
2. 剧情圣经核心部分（按 max_chars 裁剪）          ← 全局设定
3. 最近台账（load_recent_canon_entries，最近5条） ← 近期事实
4. 上一章承接信息（上一章摘要 + 正文末200字）      ← 连贯性保障
```

启用 Memory 后，4. 的历史回溯范围可以从"最近1章"扩展，
但 1-3 的拼接逻辑保持不变，Memory 作为**额外的上下文来源**自动注入。

---

## 四、文件修改清单

### 4.1 Phase 1：启用 Memory（P0，最高优先级）

| 文件 | 修改内容 | 变更类型 |
|------|---------|---------|
| `src/api.py` | 删除硬编码的 `os.environ["CREWAI_ENABLE_MEMORY"] = "false"` | 删除 |
| `src/api.py` | 改为从配置文件读取 `memory_enabled`（默认 `False`，用户主动开启） | 修改 |
| `src/generator.py` | `get_embedder_config()` 验证并修正 embedder 格式 | 修改 |
| `src/generator.py` | 启用 Memory 时增加 LanceDB 依赖检测与友好错误提示 | 新增 |
| `src/config.py` | `AppConfig` 新增 `memory_enabled: bool = False` 配置项 | 新增 |
| `requirements.txt` | 确认并添加 `lancedb` 依赖（若 CrewAI 0.75 需要） | 新增 |

### 4.2 Phase 2：添加 Agent Tools（P1）

| 文件 | 修改内容 | 变更类型 |
|------|---------|---------|
| `src/tools.py` | 新建：定义 `read_character_cards`、`read_world_settings`、`read_chapter_outline_detail`、`read_recent_chapters` 四个工具 | 新建 |
| `src/agents.py` | 为 Agent2（人物守护者）配置 `[read_character_cards, read_world_settings]` | 修改 |
| `src/agents.py` | 为 Agent3（主写手）配置 `[read_chapter_outline_detail]` | 修改 |
| `src/agents.py` | 调整 `max_iter`：Agent2=3，Agent3=3，Agent4=2 | 修改 |
| `config/agents.yaml` | 新增 `tools` 字段（用于配置驱动，Phase 2 后续迭代） | 新增 |

### 4.3 Phase 3：UI 配置开关（P1）

| 文件 | 修改内容 | 变更类型 |
|------|---------|---------|
| `gui/dialogs.py` | 在 API 设置对话框中新增"Memory 功能"开关（CheckBox）及说明文字 | 新增 |
| `gui/dialogs.py` | 新增"清理 Memory 数据"按钮（调用 Memory 清理逻辑） | 新增 |
| `src/generator.py` | 新增 `clear_project_memory(project_name)` 工具函数 | 新增 |

### 4.4 Phase 4：高级优化（P2，可选）

| 内容 | 说明 |
|------|------|
| Memory 压缩策略 | 超过20章后，将旧章节的 Memory 条目压缩为摘要级别，减少检索噪音 |
| 上下文裁剪智能化 | 根据 Memory 检索结果，动态减少 Task.description 中的历史拼接量 |
| 番茄模式 Memory 分离 | 番茄模式与标准模式使用独立的 Memory 存储路径，避免风格混淆 |

---

## 五、风险评估与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| **embedder 格式不兼容** | 高 | 高 | Phase 1 第一步验证；准备 HuggingFace 本地模型备选方案 |
| **LanceDB Windows 安装问题** | 中 | 高 | 提前测试 Windows 兼容性；失败则 fallback 到无 Memory 模式 |
| **Tools 调用增加生成时间** | 中 | 中 | 设置 `max_iter` 上限；Tool 失败时记录日志并继续（不阻断流程） |
| **Memory 检索引入噪音** | 中 | 中 | 只对章节摘要向量化（不对全文向量化），降低噪音 |
| **Memory 存储膨胀** | 低 | 低 | Phase 1 同步实现清理策略和 GUI 按钮 |
| **Tool 调用泄露项目路径** | 低 | 中 | Tools 内部使用 `project.py` 的标准路径函数，不暴露绝对路径给 Agent |

---

## 六、测试计划

### 6.1 Phase 1 验收标准

| 测试项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| Memory 开关生效 | `memory_enabled=True` 时 Crew 初始化包含 embedder | 日志中出现 embedding API 调用 |
| Memory 持久化 | 重启应用后 `.crewai/` 目录存在且有内容 | 检查目录文件 |
| Memory 跨章节检索 | 第2章生成时能检索到第1章的相关内容 | 在 verbose 模式下观察 Agent 上下文 |
| 无 Memory 降级 | embedder 不可用时自动回退到 `memory=False` | 断开 embedding API，观察是否报错 |
| 原有功能不回退 | 生成质量与现有版本持平 | 对比10章输出，人工评估 |

### 6.2 Phase 2 验收标准

| 测试项 | 验收标准 | 测试方法 |
|-------|---------|---------|
| Tools 调用成功 | 日志中出现 Tool 调用记录 | 检查 step_callback 输出 |
| Tool 失败降级 | 文件不存在时 Agent 使用 description 中的预注入内容继续 | 删除人物卡文件，观察行为 |
| 生成时间可接受 | 启用 Tools 后生成时间增加 < 30% | 计时对比（10章样本） |
| max_iter 有效 | Agent 不会无限循环调用 Tool | 观察实际 iter 次数 |

### 6.3 性能基准

| 指标 | 当前基准 | Phase 1 目标 | Phase 2 目标 |
|------|---------|-------------|-------------|
| 单章生成时间 | 基准 T | ≤ T × 1.2 | ≤ T × 1.3 |
| embedding API 调用次数/章 | 0 | ≤ 10 次 | ≤ 10 次 |
| Memory 存储大小/100章 | 0 | ≤ 200MB | ≤ 200MB |

---

## 七、关键技术结论（Quick Reference）

### 不需要做的事

| 事项 | 原因 |
|------|------|
| ❌ 手动为 Task 设置 `context` 参数传递上游输出 | `Process.sequential` 自动传递，无需手动配置 |
| ❌ 启用 `allow_delegation=True` | 当前流程职责清晰，委托场景极少，且增加调试复杂度 |
| ❌ 为 Agent1（大纲优化师）配备搜索工具 | 写作场景不依赖外部信息检索，且增加网络依赖 |
| ❌ 用 Memory 替代现有摘要+台账链路 | Memory 是补充机制，不是替代；现有确定性链路稳定性更高 |
| ❌ 一次性重构所有内容 | 渐进式改动，每个 Phase 独立验收，风险可控 |

### 需要重点关注的事

| 事项 | 说明 |
|------|------|
| ✅ 删除 `api.py` 中的 `CREWAI_ENABLE_MEMORY=false` 硬编码 | 这是 Memory 功能的主要阻塞点 |
| ✅ 验证 embedder 配置格式（CrewAI 0.75 + DashScope） | 格式错误会导致 Memory 静默失败 |
| ✅ 确认 LanceDB 在 Windows 上的依赖与路径 | Windows 路径问题是高频故障点 |
| ✅ Tools 失败时的 fallback 逻辑 | 确保 Tool 异常不阻断主流程 |
| ✅ Memory 清理 GUI 入口 | 用户需要能手动控制 Memory 大小 |

### 改动量评估

| Phase | 改动文件数 | 新增代码行数（估计） | 风险级别 |
|-------|-----------|-------------------|---------|
| Phase 1 | 4 个文件 | ~50 行 | 低（主要是删除硬编码 + 配置） |
| Phase 2 | 4 个文件 + 1 新建 | ~150 行 | 中（新增 Tools 系统） |
| Phase 3 | 2 个文件 | ~80 行 | 低（UI 配置开关） |
| Phase 4 | 待定 | 待定 | 中 |

---

## 八、附录

### A. CrewAI 0.75 Memory 相关源码入口

需要在实施前确认的代码位置：
- `crewai/crew.py`：`memory` 参数初始化逻辑
- `crewai/memory/`：Memory 后端实现（LanceDB vs ChromaDB）
- `crewai/utilities/embedder_config.py`：embedder 配置格式定义

### B. 项目目录结构（完整）

```
AI_novel/
├── main_gui.py
├── run_app.py
├── pyproject.toml              # crewai >= 0.75.0
├── requirements.txt
├── config/
│   └── agents.yaml             # 4个Agent的角色/模型/参数配置
├── src/
│   ├── generator.py            # 核心流水线（44KB）
│   ├── agents.py               # Agent工厂（9.5KB）
│   ├── tasks.py                # Task构建（15.6KB）
│   ├── api.py                  # API Key管理+模型路由（17.6KB）
│   ├── agent_factory.py        # 配置驱动Agent工厂
│   ├── config.py               # 统一配置（AppConfig数据类）
│   ├── project.py              # 项目文件管理（14.9KB）
│   ├── tools.py                # ⚡ Phase 2 新建：Agent Tools定义
│   └── services/
│       ├── chapter_service.py
│       ├── project_service.py
│       ├── api_service.py
│       └── export_service.py
├── gui/
│   ├── main_window.py          # 主窗口（39KB）
│   ├── dialogs.py              # 对话框（26KB）
│   ├── workers.py              # 后台线程
│   └── ...
└── projects/                   # 小说项目资产
    └── <project_name>/
        ├── .crewai/            # ⚡ CrewAI Memory存储目录
        ├── chapters/
        ├── summaries/
        ├── canon/
        ├── characters/
        ├── 大纲.md
        └── 剧情圣经.md
```

### C. 模型路由（现有，参考）

| 策略 | 大纲优化师 | 人物守护者 | 主写手 | 审校专家 |
|------|----------|----------|-------|---------|
| speed | DeepSeek | Qwen | Qwen | Qwen |
| balanced | DeepSeek | Qwen | Qwen | Kimi |
| quality | DeepSeek | Qwen | Kimi | Kimi |
