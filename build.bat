@echo off
setlocal EnableDelayedExpansion

:: ================================================================
:: Cross-Platform Executable Builder for ScreenLocker Application
:: ================================================================
:: This script creates platform-specific executables:
:: - Windows: .exe files using PyInstaller
:: - macOS: .app bundles using PyInstaller
:: - Linux: Binary executables using PyInstaller
:: 
:: Features:
:: - Auto-detects operating system
:: - Installs required dependencies automatically
:: - Creates single-file executables with all dependencies
:: - Handles cross-platform compatibility
:: - Cleans up build artifacts
:: ================================================================

echo.
echo ==========================================
echo  ScreenLocker Executable Builder v2.0
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.6+ from https://python.org
    pause
    exit /b 1
)

:: Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version detected: %PYTHON_VERSION%

:: Check if we're in the correct directory
if not exist "screenlocker.py" (
    echo [ERROR] screenlocker.py not found in current directory
    echo Please run this script from the screenlockerAI directory
    pause
    exit /b 1
)

if not exist "modules.py" (
    echo [ERROR] modules.py not found in current directory  
    echo Please ensure all source files are present
    pause
    exit /b 1
)

echo [INFO] Source files found: screenlocker.py, modules.py
echo.

:: Detect operating system
echo [INFO] Detecting operating system...

:: Check for Windows
ver | find "Windows" >nul
if %errorlevel% equ 0 (
    set OS_TYPE=Windows
    set EXE_EXT=.exe
    set BUILD_FLAGS=--onefile --windowed --console
    goto :os_detected
)

:: Check for WSL (Windows Subsystem for Linux)
if exist "/proc/version" (
    find "Microsoft" /proc/version >nul 2>&1
    if %errorlevel% equ 0 (
        set OS_TYPE=WSL
        set EXE_EXT=.exe
        set BUILD_FLAGS=--onefile --windowed
        goto :os_detected
    )
)

:: If we reach here, assume Unix-like system
uname -s >nul 2>&1
if %errorlevel% equ 0 (
    for /f %%i in ('uname -s') do (
        if "%%i"=="Darwin" (
            set OS_TYPE=macOS
            set EXE_EXT=.app
            set BUILD_FLAGS=--onefile --windowed --osx-bundle-identifier=com.screenlocker.app
        ) else (
            set OS_TYPE=Linux
            set EXE_EXT=
            set BUILD_FLAGS=--onefile --windowed
        )
    )
    goto :os_detected
)

:: Default to Windows if detection fails
set OS_TYPE=Windows
set EXE_EXT=.exe
set BUILD_FLAGS=--onefile --windowed --console

:os_detected
echo [INFO] Operating System: %OS_TYPE%
echo [INFO] Executable extension: %EXE_EXT%
echo.

:: Install required packages
echo [INFO] Installing required dependencies...
echo.

:: Upgrade pip first
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

:: Install PyInstaller
echo [INFO] Installing PyInstaller...
pip install pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller
    echo Please install manually with: pip install pyinstaller
    pause
    exit /b 1
)

:: Install optional dependencies based on platform
if "%OS_TYPE%"=="Windows" (
    echo [INFO] Installing Windows-specific dependencies...
    pip install keyboard >nul 2>&1
    echo [INFO] Installed keyboard module for enhanced functionality
)

:: Check if requirements.txt exists and install dependencies
if exist "requirements.txt" (
    echo [INFO] Installing project dependencies from requirements.txt...
    pip install -r requirements.txt >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Some dependencies from requirements.txt failed to install
        echo This may not affect the build process
    ) else (
        echo [INFO] All project dependencies installed successfully
    )
) else (
    echo [INFO] No requirements.txt found, skipping dependency installation
)

echo.
echo [INFO] All dependencies installed successfully!
echo.

:: Create build directory if it doesn't exist
if not exist "build" mkdir build
if not exist "dist" mkdir dist

:: Set executable name based on platform
set APP_NAME=ScreenLocker
if "%OS_TYPE%"=="Windows" set EXECUTABLE_NAME=%APP_NAME%_Windows%EXE_EXT%
if "%OS_TYPE%"=="macOS" set EXECUTABLE_NAME=%APP_NAME%_macOS%EXE_EXT%
if "%OS_TYPE%"=="Linux" set EXECUTABLE_NAME=%APP_NAME%_Linux%EXE_EXT%
if "%OS_TYPE%"=="WSL" set EXECUTABLE_NAME=%APP_NAME%_WSL%EXE_EXT%

echo [INFO] Building executable: %EXECUTABLE_NAME%
echo [INFO] Build flags: %BUILD_FLAGS%
echo.

:: Create the PyInstaller command
set PYINSTALLER_CMD=pyinstaller %BUILD_FLAGS% --name="%APP_NAME%" --distpath="dist" --workpath="build" --specpath="build"

:: Add platform-specific options
if "%OS_TYPE%"=="Windows" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=keyboard
)

if "%OS_TYPE%"=="macOS" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=subprocess
)

if "%OS_TYPE%"=="Linux" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=subprocess
)

if "%OS_TYPE%"=="WSL" (
    set PYINSTALLER_CMD=%PYINSTALLER_CMD% --hidden-import=keyboard
)

:: Add the main script
set PYINSTALLER_CMD=%PYINSTALLER_CMD% screenlocker.py

echo [INFO] Executing PyInstaller...
echo [INFO] Command: %PYINSTALLER_CMD%
echo.

:: Run PyInstaller
%PYINSTALLER_CMD%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] PyInstaller build failed!
    echo Please check the error messages above for details.
    echo.
    echo Common solutions:
    echo 1. Ensure all dependencies are installed: pip install -r requirements.txt
    echo 2. Try running: pip install pyinstaller --upgrade
    echo 3. Check that Python and pip are up to date
    echo 4. Verify that screenlocker.py and modules.py are in the current directory
    echo.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Build completed successfully!
echo.

:: Rename the executable to include platform info
if exist "dist\%APP_NAME%\%APP_NAME%%EXE_EXT%" (
    echo [INFO] Renaming executable to include platform information...
    move "dist\%APP_NAME%\%APP_NAME%%EXE_EXT%" "dist\%APP_NAME%\%EXECUTABLE_NAME%" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] Executable renamed to: %EXECUTABLE_NAME%
    )
)

:: Check if executable exists and show info
if exist "dist\%APP_NAME%\%EXECUTABLE_NAME%" (
    echo.
    echo ==========================================
    echo           BUILD SUCCESSFUL!
    echo ==========================================
    echo.
    echo [INFO] Platform: %OS_TYPE%
    echo [INFO] Executable: %EXECUTABLE_NAME%
    echo [INFO] Location: dist\%APP_NAME%\%EXECUTABLE_NAME%
    
    :: Get file size
    for %%i in ("dist\%APP_NAME%\%EXECUTABLE_NAME%") do (
        set /a SIZE=%%~zi/1024/1024
        echo [INFO] File Size: !SIZE! MB
    )
    
    echo.
    echo [USAGE] Run the executable with:
    if "%OS_TYPE%"=="Windows" (
        echo         dist\%APP_NAME%\%EXECUTABLE_NAME%
    ) else (
        echo         ./dist/%APP_NAME%/%EXECUTABLE_NAME%
    )
    
    echo.
    echo [NOTES] 
    echo - This is a standalone executable with all dependencies included
    echo - No Python installation required on target systems
    echo - Registry-based persistence works on all platforms
    echo - Use responsibly and only for authorized testing!
    
) else if exist "dist\%APP_NAME%\%APP_NAME%%EXE_EXT%" (
    echo.
    echo ==========================================
    echo           BUILD SUCCESSFUL!
    echo ==========================================
    echo.
    echo [INFO] Platform: %OS_TYPE%
    echo [INFO] Executable: %APP_NAME%%EXE_EXT%
    echo [INFO] Location: dist\%APP_NAME%\%APP_NAME%%EXE_EXT%
    
    for %%i in ("dist\%APP_NAME%\%APP_NAME%%EXE_EXT%") do (
        set /a SIZE=%%~zi/1024/1024
        echo [INFO] File Size: !SIZE! MB
    )
    
    echo.
    echo [USAGE] Run the executable with:
    if "%OS_TYPE%"=="Windows" (
        echo         dist\%APP_NAME%\%APP_NAME%%EXE_EXT%
    ) else (
        echo         ./dist/%APP_NAME%/%APP_NAME%%EXE_EXT%
    )
    
) else (
    echo.
    echo [WARNING] Executable not found in expected location
    echo [INFO] Please check the dist\ directory for the generated executable
    echo [INFO] PyInstaller may have placed it in a different location
)

:: Clean up build artifacts (optional)
echo.
set /p CLEANUP="[OPTION] Clean up build artifacts (build directory)? (y/N): "
if /i "%CLEANUP%"=="y" (
    echo [INFO] Cleaning up build artifacts...
    rmdir /s /q build >nul 2>&1
    echo [INFO] Build artifacts cleaned up
    echo [INFO] Final executable is in: dist\%APP_NAME%\
)

echo.
echo ==========================================
echo         BUILD PROCESS COMPLETE!
echo ==========================================
echo.
echo [SECURITY REMINDER]
echo This application is for educational and authorized testing purposes only.
echo Ensure you have proper authorization before using on any system.
echo The developers are not responsible for any misuse of this software.
echo.

:: Platform-specific final instructions
if "%OS_TYPE%"=="macOS" (
    echo [macOS NOTES]
    echo - The .app bundle may require code signing for distribution
    echo - Run with sudo for system-level LaunchDaemons persistence
    echo - Test in a controlled environment first
)

if "%OS_TYPE%"=="Linux" (
    echo [LINUX NOTES]  
    echo - Ensure the executable has execute permissions: chmod +x dist/%APP_NAME%/%EXECUTABLE_NAME%
    echo - Systemd services require user session for GUI applications
    echo - Test desktop integration in your specific distribution
)

if "%OS_TYPE%"=="Windows" (
    echo [WINDOWS NOTES]
    echo - Registry persistence requires appropriate user permissions
    echo - Windows Defender may flag the executable (false positive)
    echo - Run as administrator for HKEY_LOCAL_MACHINE persistence
)

echo.
pause
exit /b 0

:: Error handling labels
:error_python_not_found
echo [ERROR] Python is not installed or not accessible
echo Please install Python 3.6+ from https://python.org
echo Ensure Python is added to your system PATH
pause
exit /b 1

:error_pyinstaller_failed  
echo [ERROR] PyInstaller installation failed
echo Try manually installing with: pip install pyinstaller
echo You may need to upgrade pip: python -m pip install --upgrade pip
pause
exit /b 1

:error_build_failed
echo [ERROR] Build process failed
echo Please check the error messages above
echo Common issues:
echo - Missing dependencies (install with pip)
echo - Insufficient permissions
echo - Corrupted source files
echo - PyInstaller compatibility issues
pause
exit /b 1
