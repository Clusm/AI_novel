# 开发者指南（DEVELOPMENT）

## 1. 项目简介与架构
**AI_Novel_Writer** 是基于 PySide6 (前端) 与 CrewAI (后端智能体引擎) 构建的桌面应用程序。
项目采用前后端分离的设计思想，前端负责界面交互与状态展示，后端通过多智能体协作完成复杂的小说生成任务。

## 2. 环境准备

- 操作系统: Windows
- Python 版本: >= 3.10（见 [pyproject.toml](../pyproject.toml)）

建议使用项目根目录下的虚拟环境 `.venv/` 进行隔离开发。

## 3. 创建并激活虚拟环境

```powershell
# 创建虚拟环境
python -m venv .venv
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示脚本被禁用，请以管理员身份运行并执行：
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. 安装依赖

项目使用 `pyproject.toml` 声明依赖。在激活的虚拟环境中运行：

```powershell
python -m pip install -U pip
pip install -e .
```

## 5. 本地运行与调试

```powershell
# 运行主程序入口
python run_app.py
```

## 6. 代码导航与核心模块说明

- **GUI 界面层**: 
  - [main_gui.py](../main_gui.py): GUI 的主入口文件，负责初始化应用。
  - [gui/main_window.py](../gui/main_window.py): 核心窗口逻辑，包含所有交互、信号处理和视图渲染。
  - [gui/styles.py](../gui/styles.py): 全局 QSS 样式表，控制现代感 UI 的外观。
- **Agent 智能体层**: 
  - [src/agents.py](../src/agents.py): 定义了 Planner(大纲)、Guardian(守护)、Writer(主写)、Reviewer(终审) 等角色。
  - [src/tasks.py](../src/tasks.py): 定义了各个智能体需要执行的具体任务和Prompt指令。
- **业务逻辑层**: 
  - [src/generator.py](../src/generator.py): 核心调度器，负责协调 CrewAI 执行流、管理上下文(摘要、台账等)并输出章节。
  - [src/project.py](../src/project.py): 负责本地文件系统 IO（读写大纲、配置、日志等项目资产）。
  - [src/api.py](../src/api.py): 负责 API 密钥的安全存储与大模型连接测试。
  - [src/export.py](../src/export.py): 提供将生成内容导出为 TXT、Word、EPUB 等格式的功能。

## 7. 本地自检与打包发布

在提交代码前，建议执行语法检查：
```powershell
python -m compileall src
```

若需打包为 Windows 安装程序：
```powershell
# 运行一键打包脚本 (依赖 PyInstaller 和 Inno Setup 6)
.\build_installer.bat
```
