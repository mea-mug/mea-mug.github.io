@echo off
rem ===================================================================
rem  EXPORT FOR AI - packs the whole website into one message you can
rem  paste into any AI chat. Nothing here changes your website.
rem  Just double-click this file. There is nothing to type.
rem ===================================================================
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Make the AI prompt
chcp 65001 >nul

echo.
echo  =====================================================
echo    PACKING YOUR WEBSITE FOR THE AI
echo  =====================================================
echo.

where python >nul 2>&1
if errorlevel 1 goto :err_no_python

python "scripts\ai_export.py"
if errorlevel 1 goto :err_failed

echo.
echo  -----------------------------------------------------
echo    WHAT TO DO NOW
echo  -----------------------------------------------------
echo.
echo   1. Open  AI-PROMPT.md  (double-click it)
echo   2. Select all (Ctrl+A) and copy (Ctrl+C)
echo   3. Paste it into your AI chat
echo   4. At the BOTTOM, before sending, type what you want changed.
echo      For example:
echo        "On the contact page, change my job title to Senior Engineer."
echo        "Add a new machine to the equipment page called Pipe Bender,
echo         in the Machine tools family, using this photo:
echo         C:\Users\Otaku\Pictures\bender.jpg"
echo.
echo   5. Copy the AI's whole reply
echo   6. Paste it into  AI-RESPONSE.md  and save
echo   7. Double-click  IMPORT-FROM-AI.bat
echo.
goto :finish_ok

:err_no_python
echo.
echo  -----------------------------------------------------
echo    I COULD NOT FIND PYTHON
echo  -----------------------------------------------------
echo.
echo   This kit needs Python. Install it from https://python.org
echo   and tick "Add Python to PATH" during setup, then try again.
echo   Nothing was changed.
goto :finish_fail

:err_failed
echo.
echo  -----------------------------------------------------
echo    I COULD NOT BUILD THE PROMPT
echo  -----------------------------------------------------
echo.
echo   The message above says what went wrong.
echo   Nothing on your website was changed.
goto :finish_fail

:finish_ok
echo  Press any key to close this window.
pause >nul
exit /b 0

:finish_fail
echo.
echo  Press any key to close this window.
pause >nul
exit /b 1
