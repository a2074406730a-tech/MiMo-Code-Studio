@echo off
setlocal
cd /d "%~dp0"
echo.
echo   ============================================================
echo   =                                                          =
echo   =    MiMo Code Studio                                     =
echo   =    AI Programming Assistant                              =
echo   =                                                          =
echo   ============================================================
echo.
echo    * Author     : wuhenlol
echo    * Signature  : wuhenlol@MiMo Code Studio
echo.
echo    >> Launching...
echo.

:: Find pythonw.exe (no-console Python) via PATH
set "PYTHONW="
for /f "delims=" %%i in ('where pythonw 2^>nul') do (
    if not defined PYTHONW set "PYTHONW=%%i"
)

if defined PYTHONW (
    :: Launch with pythonw - no console window, CMD exits independently
    start "" "%PYTHONW%" main.py
    echo    Application launched! This window will close in 2 seconds...
    timeout /t 2 /nobreak >nul
) else (
    :: Fallback: python.exe (console will stay)
    echo    pythonw.exe not found, launching with python...
    python main.py
)

endlocal
