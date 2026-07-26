@echo off
rem ===================================================================
rem  IMPORT FROM AI - reads the reply you pasted into AI-RESPONSE.md
rem  and applies it to your website. Everything it touches is backed
rem  up first, into the _ai-backups folder.
rem  Just double-click this file. There is nothing to type.
rem ===================================================================
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Apply the AI reply
chcp 65001 >nul

echo.
echo  =====================================================
echo    APPLYING THE AI REPLY TO YOUR WEBSITE
echo  =====================================================
echo.

where python >nul 2>&1
if errorlevel 1 goto :err_no_python

if not exist "AI-RESPONSE.md" goto :err_no_file

python "scripts\ai_import.py"
if errorlevel 1 goto :finish_fail

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

:err_no_file
echo.
echo  -----------------------------------------------------
echo    I CANNOT FIND AI-RESPONSE.md
echo  -----------------------------------------------------
echo.
echo   Make a file called  AI-RESPONSE.md  in this folder,
echo   paste the AI's whole reply into it, save it, and run
echo   this again. Nothing was changed.
goto :finish_fail

:finish_ok
echo  Press any key to close this window.
pause >nul
exit /b 0

:finish_fail
echo.
echo  Nothing was published. If files were changed, the versions
echo  from before are in the  _ai-backups  folder.
echo.
echo  Press any key to close this window.
pause >nul
exit /b 1
