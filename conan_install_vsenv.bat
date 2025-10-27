@echo off
REM Find latest Visual Studio installation and set up environment using vswhere and vcvarsall.bat

REM Locate vswhere.exe
set VSWHERE="%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist %VSWHERE% (
    echo vswhere.exe not found. Please install Visual Studio Installer or set VSWHERE path manually.
    exit /b 1
)

REM Find latest VS installation path
for /f "usebackq tokens=*" %%i in (`%VSWHERE% -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set VSPATH=%%i
if not defined VSPATH (
    echo Visual Studio installation not found.
    exit /b 1
)

REM Find vcvars64.bat
set VCVARS="%VSPATH%\VC\Auxiliary\Build\vcvars64.bat"
if not exist %VCVARS% (
    echo vcvars64.bat not found in %VSPATH%.
    exit /b 1
)

REM Set up MSVC environment
call %VCVARS%
if errorlevel 1 (
    echo Failed to set up MSVC environment.
    exit /b 1
)

REM Run Conan install with full deployer
conan install . --build=missing --profile:a=msvc_profile --deployer=full_deploy
if errorlevel 1 (
    echo Conan install failed.
    exit /b 1
)

echo Conan install and environment setup completed successfully.
