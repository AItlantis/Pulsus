@echo off
REM Helper script to launch Pulsus console with venv activated
REM Called by pulsus_launch.bat

:: Set paths from parent script or calculate them
if not defined TESTUDO_DIR (
    for %%I in ("%~dp0\..\..\..") do set "TESTUDO_DIR=%%~fI"
)

:: Activate virtual environment
set "VENV_ACTIVATE=%TESTUDO_DIR%\venv\Scripts\activate.bat"
if exist "%VENV_ACTIVATE%" (
    call "%VENV_ACTIVATE%"
    echo [PULSUS] Virtual environment activated
) else (
    echo [PULSUS] Warning: No virtual environment found
)

:: Set PYTHONPATH
set PYTHONPATH=%TESTUDO_DIR%

:: Verify environment
@REM echo [PULSUS] Python:
@REM where python
@REM echo [PULSUS] PYTHONPATH: %PYTHONPATH%
@REM echo [PULSUS] VIRTUAL_ENV: %VIRTUAL_ENV%
@REM echo.

:: Launch console
cd /d "%TESTUDO_DIR%"
python -m agents.pulsus.console.interface

:: Pause on error
if %ERRORLEVEL% neq 0 (
    echo.
    echo [PULSUS] Console exited with error code %ERRORLEVEL%
    pause
)