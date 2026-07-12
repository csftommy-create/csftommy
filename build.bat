@echo off
REM ===============================================================
REM  Build the Windows executable (MarkSixAnalyzer.exe) via PyInstaller.
REM  Output: dist\MarkSixAnalyzer.exe  (single-file, windowed)
REM ===============================================================
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1

REM Pick the Python launcher (py preferred, else python on PATH).
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py") else (set "PY=python")

echo === Checking build dependencies ===
%PY% -m pip show pyinstaller >nul 2>nul
if not %errorlevel%==0 (
    echo Installing PyInstaller...
    %PY% -m pip install pyinstaller
    if not %errorlevel%==0 goto :fail
)

REM Ensure runtime deps are present so PyInstaller can collect them.
%PY% -c "import PySide6, pyqtgraph, requests, platformdirs" 2>nul
if not %errorlevel%==0 (
    echo Installing runtime dependencies from requirements.txt...
    %PY% -m pip install -r marksix_analyzer\requirements.txt
    if not %errorlevel%==0 goto :fail
)

echo.
echo === Cleaning previous build ===
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo === Running PyInstaller ===
%PY% -m PyInstaller --noconfirm --clean MarkSixAnalyzer.spec
if not %errorlevel%==0 goto :fail

echo.
if exist "dist\MarkSixAnalyzer.exe" (
    echo === BUILD SUCCEEDED ===
    echo Executable: %~dp0dist\MarkSixAnalyzer.exe
    for %%F in ("dist\MarkSixAnalyzer.exe") do echo Size: %%~zF bytes
) else (
    echo Build finished but dist\MarkSixAnalyzer.exe was not found.
    goto :fail
)

echo.
pause
endlocal
exit /b 0

:fail
echo.
echo *** BUILD FAILED ***  See the messages above.
echo.
pause
endlocal
exit /b 1
