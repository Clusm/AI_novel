# AI 小说写作系统（AI Novel Factory）

基于 Streamlit + CrewAI 的多智能体网文写作流水线：从大纲出发，自动生成章节正文，并提供一致性维护（剧情圣经/章节摘要/事实台账）、项目管理与多格式导出。

## 主要特性

- 多项目管理：每本书独立存储大纲、章节、摘要、日志等资产
- 多 Agent 流水线：提纲 → 设定守护 → 爽点 → 主写 → 终审（审查+润色）
- 一致性资产：
  - 剧情圣经：从大纲提炼的全局设定资产（世界观/人物卡/伏笔表等）
  - 章节摘要：每章自动生成并作为下一章强连续性输入
  - 事实台账：每章沉淀“不可逆事实/状态变更/资源变更/锚点”
- 章节成品规范：
  - 终审定稿自动去除章节内情节标题（只保留 `# 第N章 标题`）
  - 正文长度自动保障（默认 ≥3500 字，自动扩写补足）
- API Key 安全存储：加密保存到本地文件（不写入代码）
- 导出：TXT / Word（docx）/ EPUB

## 快速开始（普通用户）

1. 运行 `dist/AI_Novel_Writer.exe`
2. 浏览器自动打开页面（首次启动可能需要 30–60 秒）
3. 在侧边栏配置 API Key（DeepSeek / 通义千问 / Kimi 可选）
4. 新建项目 → 粘贴大纲 → 生成章节

更详细的使用步骤见：[docs/USAGE.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/USAGE.md)

## 快速开始（开发者）

### 环境要求

- Windows
- Python >= 3.10（项目声明在 [pyproject.toml](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/pyproject.toml)）

### 安装与启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
pip install -e .

streamlit run app.py
```

如果 PowerShell 无法激活虚拟环境（脚本策略限制）：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

开发说明见：[docs/DEVELOPMENT.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/DEVELOPMENT.md)

## 文档导航

- 使用指南：[docs/USAGE.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/USAGE.md)
- 一致性与可控：[docs/CONSISTENCY.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/CONSISTENCY.md)
- 架构与工作原理：[docs/ARCHITECTURE.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/ARCHITECTURE.md)
- 打包与发布：[docs/PACKAGING.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/PACKAGING.md)
- 常见问题：[docs/FAQ.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/docs/FAQ.md)

历史文档（仍保留在根目录）：

- [使用教程.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/使用教程.md)
- [项目说明.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/项目说明.md)
- [技术工作原理.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/技术工作原理.md)
- [可控与一致性维护.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/可控与一致性维护.md)
- [大纲模板（参考）.md](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/大纲模板（参考）.md)

## 项目结构

```text
AI_novel/
├── app.py                       Streamlit UI 入口
├── run_app.py                   本地启动脚本（EXE/源码共用）
├── src/                         核心逻辑（Agent/Task/生成/导出/项目资产）
├── projects/                    小说项目资产目录（大纲/章节/摘要/台账/圣经）
├── dist/                        打包产物（可选）
├── AI_Novel_Writer.spec         PyInstaller 打包配置
└── build_exe.bat                一键打包脚本（可选）
```

## 安全提示

- API 配置会写入：
  - `.api_keys.enc`（密文）
  - `.encryption_key`（本机对称密钥）
- 不要把上述两类文件提交到公共仓库或发送给他人。

## 致谢

- CrewAI
- Streamlit
- LiteLLM
