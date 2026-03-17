@echo off
setlocal

:: ========================================================
:: AI Novel Writer - One-Click Build Script
:: ========================================================

echo [1/3] Checking environment...
:: Check if PyInstaller is in PATH
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: PyInstaller is not installed or not in PATH.
    echo Please install it using: pip install pyinstaller
    pause
    exit /b 1
)

:: Check Inno Setup Path
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" (
    echo Error: Inno Setup Compiler not found at:
    echo "%ISCC_PATH%"
    echo Please verify Inno Setup 6 installation path.
    pause
    exit /b 1
)

echo.
echo [2/3] Running PyInstaller...
echo This may take a few minutes...
:: Clean previous build artifacts
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

pyinstaller AI_Novel_Writer.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo.
    echo Error: PyInstaller build failed!
    pause
    exit /b %errorlevel%
)
echo PyInstaller build successful.

echo.
echo [3/3] Compiling Installer with Inno Setup...
"%ISCC_PATH%" "AI_Novel_Writer.iss"
if %errorlevel% neq 0 (
    echo.
    echo Error: Inno Setup compilation failed!
    pause
    exit /b %errorlevel%
)

echo.
echo ========================================================
echo       BUILD SUCCESSFUL!
echo ========================================================
echo Installer created at: Output\AI_Novel_Writer_Setup_v2.4.exe
echo.
pause
