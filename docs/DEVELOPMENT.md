# 开发者指南（DEVELOPMENT）

## 环境准备

- Windows
- Python >= 3.10（见 [pyproject.toml](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/pyproject.toml)）

建议使用项目根目录下的虚拟环境 `.venv/`。

## 创建并激活虚拟环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示脚本被禁用：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 安装依赖

项目使用 `pyproject.toml` 声明依赖：

```powershell
python -m pip install -U pip
pip install -e .
```

## 本地运行

```powershell
python run_app.py
```

## 代码导航

- UI： [main_gui.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/main_gui.py) + [gui/](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/gui)
- Agent 定义： [agents.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/agents.py)
- Task 定义： [tasks.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/tasks.py)
- 章节生成与编排： [generator.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/generator.py)
- 项目资产 IO： [project.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/project.py)
- API Key 加密存储与测试： [api.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/api.py)
- 导出： [export.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/src/export.py)

## 本地自检

当前仓库未提供统一的测试命令入口时，可至少执行语法编译检查：

```powershell
python -m compileall src
```
