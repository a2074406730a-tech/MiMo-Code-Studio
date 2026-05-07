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
echo    * Model      : mimo-v2.5-pro
echo    * Framework  : customtkinter + edge-tts
echo    * Directory  : %~dp0
echo    * Author     : wuhenlol
echo    * Signature  : wuhenlol@MiMo Code Studio
echo.
echo    >> Launching...
echo.
start "MiMo Code Studio" python main.py
endlocal
