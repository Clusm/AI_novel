# 打包与发布指南 (PACKAGING)

本项目使用 **PyInstaller (onedir 模式)** + **Inno Setup** 的组合方式进行打包发布。这种方式生成的安装包体验更专业，启动速度更快，且更易于分发。

---

## 1. 核心配置文件

- **PyInstaller 配置**: `AI_Novel_Writer.spec`
  - 模式: `onedir` (生成包含 EXE 和依赖文件的文件夹)
  - 入口: `run_app.py`
  - 包含资源: `src/`, `gui/`, 以及 CrewAI/ChromaDB 等核心库的资源文件
- **Inno Setup 脚本**: `AI_Novel_Writer.iss`
  - 输入: `dist/AI_Novel_Writer/` 目录
  - 输出: `Output/AI_Novel_Writer_Setup_vX.X.exe` 安装包

---

## 2. 打包步骤

### 快速打包 (推荐)

在项目根目录下双击运行 `build_installer.bat` 脚本即可一键完成所有打包步骤。

该脚本会自动：
1. 清理旧的构建文件
2. 运行 PyInstaller 生成可执行文件
3. 调用 Inno Setup 编译器生成最终安装包

---

### 手动打包步骤 (高级)

#### 第一步：构建可执行文件目录 (PyInstaller)

在项目根目录下运行：

```powershell
# 确保已激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 清理旧构建 (可选，推荐)
Remove-Item -Recurse -Force dist, build

# 执行打包
pyinstaller AI_Novel_Writer.spec
```

成功后，你将在 `dist/AI_Novel_Writer/` 目录下看到 `AI_Novel_Writer.exe` 和大量依赖文件。你可以直接运行该 EXE 进行测试。

### 第二步：制作安装包 (Inno Setup)

1. 确保已安装 [Inno Setup](https://jrsoftware.org/isdl.php)。
2. 右键点击项目根目录下的 `AI_Novel_Writer.iss`，选择 **"Compile"**。
3. 或者在命令行运行：
   ```powershell
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" AI_Novel_Writer.iss
   ```

编译完成后，安装包将生成在 `Output/` 目录下，例如 `AI_Novel_Writer_Setup_v2.4.exe`。

---

## 3. 常见问题 (FAQ)

### Q: 为什么不用 `onefile` (单文件 EXE)?
A: `onefile` 模式在启动时需要解压所有依赖到临时目录，导致启动非常缓慢（尤其是包含 CrewAI/ChromaDB 这种大型库时，启动可能需要 30-60 秒）。`onedir` 模式启动极快，且配合安装包使用体验更好。

### Q: 打包后体积为什么很大？
A: 项目依赖了 CrewAI、LangChain、ChromaDB 等 AI 框架，这些库本身体积较大且包含许多二进制依赖（如 SQLite, NumPy 等）。这是正常现象。

### Q: 运行报错 "Permission denied"?
A: 请确保：
1. 没有其他程序（如 VS Code, 终端）正在占用 `dist/` 目录下的文件。
2. 安装后运行时，程序会尝试写入用户数据。我们已将数据存储路径迁移至 `%APPDATA%\AI_Novel_Writer` 和 `Documents\AI_Novel_Projects`，避免写入 `Program Files` 导致的权限问题。
