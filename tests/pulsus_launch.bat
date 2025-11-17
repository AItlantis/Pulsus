@echo off
REM =====================================================================
REM  PULSUS AGENT — LAUNCH, TEST, AND VENV-AWARE CONSOLE SCRIPT
REM =====================================================================
:: Enable UTF-8 output
chcp 65001 >nul

title [PULSUS QA] Agent Test - Launch

:: Navigate to project root (from tests folder)
:: We're in testudo/agents/pulsus/tests, go up to Atlantis root
for %%I in ("%~dp0\..\..\..\..") do set "ROOT_DIR=%%~fI"
for %%I in ("%~dp0\..\..\..") do set "TESTUDO_DIR=%%~fI"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║           PULSUS AGENT TEST - CONSOLE LAUNCHER           ║
echo ╚══════════════════════════════════════════════════════════╝
echo Root: %ROOT_DIR%
echo Testudo: %TESTUDO_DIR%
echo --------------------------------------------------------------
echo.

:: 1️⃣ Check for virtual environment and activate it
set "VENV_ACTIVATE=%TESTUDO_DIR%\venv\Scripts\activate.bat"
if exist "%VENV_ACTIVATE%" (
    echo [TESTUDO]Activating virtual environment...
    call "%VENV_ACTIVATE%"
    echo [TESTUDO]✅ Virtual environment activated.
) else (
    echo [TESTUDO]⚠ No virtual environment found, using system Python...
)
echo.

:: 2️⃣ Set PYTHONPATH so all packages are discoverable
set PYTHONPATH=%TESTUDO_DIR%
set PYTEST_DISABLE_PLUGIN_AUTOLOAD=1

:: Verify Python location
echo [INFO] Using Python from:
where python
echo [INFO] PYTHONPATH=%PYTHONPATH%
echo.

:: 3️⃣ Environment Check (Ollama)
echo.
echo [STEP 3] Checking Ollama environment...
echo --------------------------------------------------------------
pytest -p no:qt -q "%TESTUDO_DIR%\agents\pulsus\tests\test_ollama_env.py" --disable-warnings
set OLLAMA_CHECK=%ERRORLEVEL%

if %OLLAMA_CHECK% neq 0 (
    echo.
    echo [TESTUDO]⚠ Ollama not detected or not responding.
    echo [TESTUDO]Attempting to start Ollama in background...
    echo --------------------------------------------------------------
    start "" /MIN ollama serve
    timeout /t 5 >nul
    echo [INFO] Re-running environment test...
    pytest -p no:qt -q "%TESTUDO_DIR%\agents\pulsus\tests\test_ollama_env.py" --disable-warnings
    set OLLAMA_CHECK=%ERRORLEVEL%

    if %OLLAMA_CHECK% neq 0 (
        echo.
        color 0C
        echo [ERROR] Ollama failed to start or respond after retry.
        echo [ACTION] Please run manually:  ollama serve
        echo [INFO]  Download from: https://ollama.ai
        echo --------------------------------------------------------------
        pause
        exit /b 1
    ) else (
        @REM color 0A
        echo [OK] Ollama successfully started and verified.
    )
) else (
    @REM color 0A
    echo [OK] Ollama environment is healthy and running.
)
echo --------------------------------------------------------------

:: 4️⃣ Run unit tests
echo [TESTUDO]Running unit tests...
cd /d "%TESTUDO_DIR%"
pytest -p no:qt -q agents/pulsus/tests --disable-warnings
if %errorlevel% neq 0 (
    echo [TESTUDO]❌ Unit tests failed. See above for details.
    pause
    exit /b 1
)
cd /d "%~dp0"
echo [TESTUDO]✅ All tests passed successfully.
echo.

:: 5️⃣ Launch Pulsus console inside VENV
echo [TESTUDO]Preparing to launch agent console...
set "CONSOLE_CMD=python -m agents.pulsus.console.interface"

:: Ensure the interface script exists
if not exist "%TESTUDO_DIR%\agents\pulsus\console\interface.py" (
    echo [TESTUDO]❌ Cannot find interface.py. Expected at:
    echo     %TESTUDO_DIR%\agents\pulsus\console\interface.py
    pause
    exit /b 1
)

:: Launch console in new window using helper script
echo [TESTUDO]Launching console with virtual environment...
start "PULSUS AGENT" cmd /k "%~dp0launch_console.bat"

echo [TESTUDO]Console started in new window.
pause
exit /b 0