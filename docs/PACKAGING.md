# 打包与发布（PACKAGING）

本项目当前使用 PyInstaller 打包为 Windows 可执行文件（EXE）。由于依赖栈较重（CrewAI + ChromaDB + 导出组件），onefile 体积会明显偏大。

## 当前打包方式（onefile）

核心配置文件：

- [AI_Novel_Writer.spec](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/AI_Novel_Writer.spec)

特征：

- `onefile`：生成单个 EXE，首次启动会解压依赖，启动慢但分发简单
- `collect_all()`：对 crewai / chromadb / langchain / tiktoken / litellm / docx / ebooklib 等进行资源收集，体积增长明显
- `upx=True`：能压缩一部分体积，但对某些二进制依赖的收益有限

## 降体积的推荐路线

### 路线 A：onedir + 安装包（推荐）

思路：

- 先用 PyInstaller 生成 `onedir` 目录版（EXE + 依赖文件夹）
- 再用安装包工具（Inno Setup / NSIS / WiX）制作“点击安装”的安装程序
- 安装程序负责：
  - 复制文件到 `{localappdata}\Programs\AI_Novel_Writer` 或 `Program Files`
  - 创建开始菜单与桌面快捷方式

收益：

- 启动速度更快（不需要每次自解压）
- 安装体验更像“正式软件”
- 总体体积不一定变小，但分发更可控，用户感知更好

### 路线 B：继续 onefile，但做依赖裁剪（高级）

思路：

- 尽量减少 `collect_all()` 的范围与 hiddenimports
- 排除不需要的可选依赖（例如：不用某些导出格式就去掉相关库）

风险：

- 裁剪过度会导致运行时 ImportError，排查成本高

## 可执行体积为什么会大

主要原因：

- CrewAI/ChromaDB/向量检索相关依赖体积大
- 文档导出依赖（python-docx、ebooklib、pypandoc 等）会额外引入资源
- Windows 下的 python runtime、扩展模块、证书等都会打入包内

## 构建建议

- 生成环境尽量干净：只安装本项目依赖，避免把无关包打进产物
- 确认 `dist/` 与 `build/` 中间产物在打包前清理干净
- 打包失败提示“拒绝访问”：检查目标 EXE 是否正在运行

与 EXE 启动相关的逻辑在：

- [run_app.py](file:///c:/Users/Tao/Documents/trae_projects/AI_novel/run_app.py)

它负责在 EXE 模式下启动 PySide6 应用程序。
