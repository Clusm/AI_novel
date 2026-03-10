@echo off
chcp 65001 >nul
setlocal EnableExtensions
pushd "%~dp0"
echo ========================================================
echo        AI 小说写作系统 - 一键打包工具
echo ========================================================
echo.

echo [1/4] 正在检查环境...
set "PYEXE="
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"
if "%PYEXE%"=="" (
    where python >nul 2>&1
    if %errorlevel% equ 0 set "PYEXE=python"
)
if "%PYEXE%"=="" (
    echo 错误: 未检测到 Python。
    echo - 推荐做法：在当前目录创建虚拟环境 .venv，然后再双击本脚本。
    echo - 或确保系统已安装 Python 并加入 PATH。
    if not defined NO_PAUSE pause
    exit /b 1
)
"%PYEXE%" --version

echo [2/4] 正在安装打包工具 (PyInstaller)...
"%PYEXE%" -m pip install pyinstaller -q
if %errorlevel% neq 0 (
    echo 错误: PyInstaller 安装失败。
    if not defined NO_PAUSE pause
    exit /b 1
)

echo [3/4] 正在构建可执行文件（这可能需要几分钟）...
echo.

if not exist "favicon.ico" (
    echo 错误: 未找到 favicon.ico，请将图标放在项目根目录再重试。
    if not defined NO_PAUSE pause
    exit /b 1
)

taskkill /F /IM AI_Novel_Writer.exe >nul 2>&1

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Run PyInstaller
"%PYEXE%" -m PyInstaller --noconfirm --onefile --windowed --clean ^
    --name "AI_Novel_Writer" ^
    --icon "favicon.ico" ^
    --collect-all streamlit ^
    --collect-all crewai ^
    --collect-all chromadb ^
    --collect-all langchain ^
    --collect-all tiktoken ^
    --collect-all litellm ^
    --collect-all docx ^
    --collect-all ebooklib ^
    --hidden-import streamlit ^
    --hidden-import litellm ^
    --hidden-import tiktoken_ext.openai_public ^
    --hidden-import tiktoken_ext ^
    --add-data "app.py;." ^
    --add-data "src;src" ^
    run_app.py

if %errorlevel% neq 0 (
    echo.
    echo 错误: 构建失败！
    if not defined NO_PAUSE pause
    exit /b 1
)

echo.
echo [4/4] 构建成功！
echo.
echo 可执行文件位于: dist\AI_Novel_Writer.exe
echo.
echo 你现在可以将 "dist\AI_Novel_Writer.exe" 复制到任何文件夹运行。
echo 注意: 首次运行可能需要几十秒进行解压，请耐心等待。
echo.
if not defined NO_PAUSE pause
popd
