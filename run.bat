@echo off
REM ---------------------------------------------------------------
REM  MarkSix Analyzer launcher (Windows)
REM  Double-click this file, or run "run.bat" from a terminal.
REM ---------------------------------------------------------------
setlocal
cd /d "%~dp0"

REM Force UTF-8 so Traditional Chinese output/logging renders correctly.
set PYTHONUTF8=1

REM Prefer the Python launcher (py); fall back to python on PATH.
where py >nul 2>nul
if %errorlevel%==0 (
    set "PY=py"
) else (
    set "PY=python"
)

echo Starting MarkSix Analyzer...
%PY% run.py %*
set "EXITCODE=%errorlevel%"

if not "%EXITCODE%"=="0" (
    echo.
    echo The app exited with error code %EXITCODE%.
    echo If this is a missing-dependency error, run:
    echo     %PY% -m pip install -r marksix_analyzer\requirements.txt
    echo.
    pause
)

endlocal
exit /b %EXITCODE%
