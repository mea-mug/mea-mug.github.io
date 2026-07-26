@echo off
rem ===================================================================
rem  ADMIN - opens your website control panel in the browser.
rem  Everything is here: build the AI prompt, apply the AI's reply,
rem  preview the site, and publish it.
rem  Just double-click this file. There is nothing to type.
rem ===================================================================
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Website Admin
chcp 65001 >nul

echo.
echo  =====================================================
echo    WEBSITE ADMIN
echo  =====================================================

where python >nul 2>&1
if errorlevel 1 goto :err_no_python

if not exist "scripts\admin_server.py" goto :err_missing
if not exist "scripts\admin.html" goto :err_missing

python "scripts\admin_server.py"
if errorlevel 1 goto :finish_fail
goto :finish_ok

:err_no_python
echo.
echo  -----------------------------------------------------
echo    I COULD NOT FIND PYTHON
echo  -----------------------------------------------------
echo.
echo   This kit needs Python. Install it from https://python.org
echo   and tick "Add Python to PATH" during setup, then try again.
goto :finish_fail

:err_missing
echo.
echo  -----------------------------------------------------
echo    PART OF THE ADMIN PAGE IS MISSING
echo  -----------------------------------------------------
echo.
echo   I need both of these files:
echo     scripts\admin_server.py
echo     scripts\admin.html
echo.
echo   Get a fresh copy of them, then try again.
goto :finish_fail

:finish_ok
echo.
echo  The admin page has shut down.
echo  Press any key to close this window.
pause >nul
exit /b 0

:finish_fail
echo.
echo  Press any key to close this window.
pause >nul
exit /b 1
