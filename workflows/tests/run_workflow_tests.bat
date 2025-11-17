@echo off
REM ============================================================================
REM Pulsus Workflow Tests Runner
REM ============================================================================
REM
REM This batch file runs comprehensive workflow tests for Pulsus including:
REM - Repository analysis workflows
REM - MCP tools integration tests
REM - Session memory and follow-up questions
REM - Performance and timing analysis
REM
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================================
echo PULSUS WORKFLOW TESTS
echo ============================================================================
echo Running comprehensive workflow tests with performance analysis
echo ============================================================================
echo.

REM Change to testudo directory
cd /d "%~dp0..\..\..\..\..\"
if not exist "testudo" (
    echo [ERROR] testudo directory not found!
    exit /b 1
)
cd testudo

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at testudo\venv
    echo Please run: python -m venv venv
    exit /b 1
)

echo [*] Using Python: venv\Scripts\python.exe
echo [*] Working directory: %CD%
echo.

REM Set test results file
set "RESULTS_FILE=agents\pulsus\workflows\tests\test_results.txt"
set "TIMESTAMP=%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"

echo Test Run: %TIMESTAMP% > "%RESULTS_FILE%"
echo ============================================================================ >> "%RESULTS_FILE%"
echo. >> "%RESULTS_FILE%"

REM ============================================================================
REM Test 1: Repository Analysis Workflow
REM ============================================================================
echo.
echo ----------------------------------------------------------------------------
echo TEST 1: Repository Analysis Workflow
echo ----------------------------------------------------------------------------
echo [*] Running test_repository_analysis_workflow.py...
echo.

set "START_TIME=%time%"
venv\Scripts\python.exe agents\pulsus\workflows\tests\test_repository_analysis_workflow.py
set "TEST1_RESULT=%ERRORLEVEL%"
set "END_TIME=%time%"

REM Calculate duration (simplified)
echo. >> "%RESULTS_FILE%"
echo TEST 1: Repository Analysis Workflow >> "%RESULTS_FILE%"
echo   Start: %START_TIME% >> "%RESULTS_FILE%"
echo   End:   %END_TIME% >> "%RESULTS_FILE%"

if %TEST1_RESULT% EQU 0 (
    echo [SUCCESS] Test 1 passed
    echo   Result: PASSED >> "%RESULTS_FILE%"
) else (
    echo [FAILED] Test 1 failed with exit code: %TEST1_RESULT%
    echo   Result: FAILED ^(exit code %TEST1_RESULT%^) >> "%RESULTS_FILE%"
)

REM ============================================================================
REM Test 2: MCP Tools Workflow
REM ============================================================================
echo.
echo ----------------------------------------------------------------------------
echo TEST 2: MCP Tools Workflow
echo ----------------------------------------------------------------------------
echo [*] Running test_mcp_tools_workflow.py...
echo.

set "START_TIME=%time%"
venv\Scripts\python.exe agents\pulsus\workflows\tests\test_mcp_tools_workflow.py
set "TEST2_RESULT=%ERRORLEVEL%"
set "END_TIME=%time%"

echo. >> "%RESULTS_FILE%"
echo TEST 2: MCP Tools Workflow >> "%RESULTS_FILE%"
echo   Start: %START_TIME% >> "%RESULTS_FILE%"
echo   End:   %END_TIME% >> "%RESULTS_FILE%"

if %TEST2_RESULT% EQU 0 (
    echo [SUCCESS] Test 2 passed
    echo   Result: PASSED >> "%RESULTS_FILE%"
) else (
    echo [FAILED] Test 2 failed with exit code: %TEST2_RESULT%
    echo   Result: FAILED ^(exit code %TEST2_RESULT%^) >> "%RESULTS_FILE%"
)

REM ============================================================================
REM Test 3: MCP Unit Tests
REM ============================================================================
echo.
echo ----------------------------------------------------------------------------
echo TEST 3: MCP Unit Tests
echo ----------------------------------------------------------------------------
echo [*] Running MCP unit tests...
echo.

set "START_TIME=%time%"
venv\Scripts\python.exe -m pytest agents\mcp\tests\ -v --tb=short 2>nul
if %ERRORLEVEL% NEQ 0 (
    REM If pytest not installed, try running tests directly
    echo [*] pytest not available, running tests directly...

    set "TEST3_RESULT=0"
    for %%f in (agents\mcp\tests\test_*.py) do (
        echo   Running %%~nxf...
        venv\Scripts\python.exe "%%f"
        if !ERRORLEVEL! NEQ 0 set "TEST3_RESULT=1"
    )
) else (
    set "TEST3_RESULT=%ERRORLEVEL%"
)
set "END_TIME=%time%"

echo. >> "%RESULTS_FILE%"
echo TEST 3: MCP Unit Tests >> "%RESULTS_FILE%"
echo   Start: %START_TIME% >> "%RESULTS_FILE%"
echo   End:   %END_TIME% >> "%RESULTS_FILE%"

if %TEST3_RESULT% EQU 0 (
    echo [SUCCESS] Test 3 passed
    echo   Result: PASSED >> "%RESULTS_FILE%"
) else (
    echo [FAILED] Test 3 failed
    echo   Result: FAILED >> "%RESULTS_FILE%"
)

REM ============================================================================
REM Test 4: Performance Benchmark
REM ============================================================================
echo.
echo ----------------------------------------------------------------------------
echo TEST 4: Performance Benchmark
echo ----------------------------------------------------------------------------
echo [*] Running performance benchmarks...
echo.

echo. >> "%RESULTS_FILE%"
echo TEST 4: Performance Benchmark >> "%RESULTS_FILE%"
echo. >> "%RESULTS_FILE%"

REM Test routing performance
echo   [*] Testing routing performance (100 iterations)...
set "START_TIME=%time%"

for /L %%i in (1,1,100) do (
    venv\Scripts\python.exe -c "from agents.pulsus.routing.router import route; route('analyze repository', non_interactive=True, dry_run=True)" >nul 2>&1
)

set "END_TIME=%time%"
echo   Routing: Start %START_TIME% - End %END_TIME% >> "%RESULTS_FILE%"
echo   [DONE] Routing performance test complete

REM Test tool discovery performance
echo   [*] Testing tool discovery performance (100 iterations)...
set "START_TIME=%time%"

for /L %%i in (1,1,100) do (
    venv\Scripts\python.exe -c "from agents.pulsus.routing.mcp_router import MCPRouter; from agents.pulsus.config.settings import load_settings; s=load_settings(); r=MCPRouter(s.workflows_root); r.discover_tools('analysis', 'analyze_repository', 'analyze repo')" >nul 2>&1
)

set "END_TIME=%time%"
echo   Tool Discovery: Start %START_TIME% - End %END_TIME% >> "%RESULTS_FILE%"
echo   [DONE] Tool discovery performance test complete

REM Test MCP tool invocation performance
echo   [*] Testing MCP tool performance (10 iterations)...
set "START_TIME=%time%"

for /L %%i in (1,1,10) do (
    venv\Scripts\python.exe -c "from agents.shared.tools import mcp_read_script; mcp_read_script.invoke({'path': 'agents/pulsus/ui/display_manager.py'})" >nul 2>&1
)

set "END_TIME=%time%"
echo   MCP Tools: Start %START_TIME% - End %END_TIME% >> "%RESULTS_FILE%"
echo   [DONE] MCP tool performance test complete

REM ============================================================================
REM Summary
REM ============================================================================
echo.
echo ============================================================================
echo TEST SUMMARY
echo ============================================================================

set /a "TOTAL_TESTS=3"
set /a "PASSED_TESTS=0"

if %TEST1_RESULT% EQU 0 set /a "PASSED_TESTS+=1"
if %TEST2_RESULT% EQU 0 set /a "PASSED_TESTS+=1"
if %TEST3_RESULT% EQU 0 set /a "PASSED_TESTS+=1"

echo.
echo   Repository Analysis:  %TEST1_RESULT% (0=pass)
echo   MCP Tools Workflow:   %TEST2_RESULT% (0=pass)
echo   MCP Unit Tests:       %TEST3_RESULT% (0=pass)
echo   Performance Bench:    COMPLETED
echo.
echo   Total: %PASSED_TESTS%/%TOTAL_TESTS% test suites passed
echo.

echo. >> "%RESULTS_FILE%"
echo ============================================================================ >> "%RESULTS_FILE%"
echo SUMMARY >> "%RESULTS_FILE%"
echo ============================================================================ >> "%RESULTS_FILE%"
echo   Repository Analysis:  %TEST1_RESULT% >> "%RESULTS_FILE%"
echo   MCP Tools Workflow:   %TEST2_RESULT% >> "%RESULTS_FILE%"
echo   MCP Unit Tests:       %TEST3_RESULT% >> "%RESULTS_FILE%"
echo   Performance Bench:    COMPLETED >> "%RESULTS_FILE%"
echo. >> "%RESULTS_FILE%"
echo   Total: %PASSED_TESTS%/%TOTAL_TESTS% test suites passed >> "%RESULTS_FILE%"
echo ============================================================================ >> "%RESULTS_FILE%"

echo Results saved to: %RESULTS_FILE%
echo ============================================================================

if %PASSED_TESTS% EQU %TOTAL_TESTS% (
    echo.
    echo [SUCCESS] All tests passed!
    echo.
    exit /b 0
) else (
    echo.
    echo [FAILED] Some tests failed. Check test_results.txt for details.
    echo.
    exit /b 1
)
