# 架构与数据流（ARCHITECTURE）

本项目可以理解为三层：交互层（Streamlit UI）、编排层（CrewAI 多 Agent 流水线）、资产层（projects/ + 本地记忆库）。

## 模块分层

- 交互层： [app.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/app.py)
- 编排层： [generator.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/generator.py)、[agents.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/agents.py)、[tasks.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/tasks.py)
- 资产层： [project.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/project.py)、`projects/<项目名>/`

## 章节生成数据流

```text
UI 输入大纲（保存到 projects/<项目名>/大纲.md）
  ↓
生成器加载/更新剧情圣经（projects/<项目名>/剧情圣经.md）
  ↓
拼装强连续性输入：
  - 上一章摘要（summaries/）
  - 最近章节事实台账（canon/）
  ↓
创建 5 个任务并顺序执行（Process.sequential）：
  1) 大纲动态优化师：本章详细提纲
  2) 人物与世界观守护者：一致性护栏
  3) 爽点强化设计师：爽点方案
  4) 章节主写手：正文 + 摘要块
  5) 终极审校专家：一致性 Gate + 润色（并剥离摘要块）
  ↓
保存资产：
  - chapters/第N章.md（最终正文）
  - summaries/第N章摘要.md（摘要）
  - canon/第N章台账.md（事实台账）
```

## 资产目录约定（projects/<项目名>/）

- `大纲.md`：用户输入大纲
- `剧情圣经.md`：系统从大纲提炼/增量更新的全局设定资产
- `chapters/`：章节正文（成品仅保留章标题，不含情节分段标题）
- `summaries/`：章节摘要（下一章强连续性输入）
- `canon/`：事实台账（不可逆事实/状态变更/资源变更/锚点）
- `logs/`：运行日志

更详细的长文说明见：

- [项目说明.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/项目说明.md)
- [技术工作原理.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/技术工作原理.md)
