@echo off
setlocal

echo ========================================
echo  ChemMaster Build ^& Package Script
echo ========================================
echo.

:: Check prerequisites
where wails >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Wails CLI not found. Install with: go install github.com/wailsapp/wails/v2/cmd/wails@latest
    exit /b 1
)

where go >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Go not found. Install from https://go.dev/dl/
    exit /b 1
)

:: Step 1: Build Wails application
echo [1/3] Building Wails application...
wails build
if errorlevel 1 (
    echo [ERROR] Wails build failed.
    exit /b 1
)
echo       Done: build\bin\ChemMaster.exe
echo.

:: Step 2: Check for Inno Setup
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if "%ISCC%"=="" (
    echo [2/3] Inno Setup not found. Skipping installer compilation.
    echo       To build the installer, install Inno Setup 6 from:
    echo       https://jrsoftware.org/isinfo.php
    echo       Then run: "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer\ChemMaster.iss
    goto :end
)

:: Step 3: Compile installer
echo [2/3] Compiling installer with Inno Setup...
mkdir build\installer 2>nul
"%ISCC%" installer\ChemMaster.iss
if errorlevel 1 (
    echo [ERROR] Installer compilation failed.
    exit /b 1
)
echo       Done: build\installer\ChemMaster-Setup-1.0.2.exe
echo.

:end
echo ========================================
echo  Build complete!
echo ========================================
echo.
echo  Application:  build\bin\ChemMaster.exe
if exist "build\installer\ChemMaster-Setup-1.0.2.exe" (
    echo  Installer:    build\installer\ChemMaster-Setup-1.0.2.exe
)
echo.
endlocal
