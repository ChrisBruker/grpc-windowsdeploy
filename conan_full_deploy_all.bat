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

REM Run Conan install for Release
conan install . --build=missing --profile:a=msvc_release --deployer=full_deploy
if errorlevel 1 (
    echo Conan install failed for Release.
    exit /b 1
)

REM Run Conan install for Debug
conan install . --build=missing --profile:a=msvc_debug --deployer=full_deploy
if errorlevel 1 (
    echo Conan install failed for Debug.
    exit /b 1
)

REM Run Conan install for RelWithDebInfo
conan install . --build=missing --profile:a=msvc_release -s build_type=RelWithDebInfo --deployer=full_deploy
if errorlevel 1 (
    echo Conan install failed for RelWithDebInfo.
    exit /b 1
)

REM Copy the generated CMake files for consumers without Conan
set GENERATORS_DIR=%~dp0build\generators
set DEPLOY_CMAKE_DIR=%~dp0full_deploy\cmake
set ROBOCODE=0
if exist "%GENERATORS_DIR%" (
    echo Copying generated CMake files to %DEPLOY_CMAKE_DIR%
    robocopy "%GENERATORS_DIR%" "%DEPLOY_CMAKE_DIR%" /E >nul
    set ROBOCODE=%ERRORLEVEL%
)

if %ROBOCODE% GEQ 8 (
    echo Failed to copy generated CMake files.
    exit /b %ROBOCODE%
)

echo Conan install and environment setup completed successfully for all configurations.
exit /b 0
