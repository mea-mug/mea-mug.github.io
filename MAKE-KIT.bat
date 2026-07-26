@echo off
rem ===================================================================
rem  MAKE KIT - builds a clean copy of this kit that you can give to
rem  someone else. It copies only the kit itself: none of your own web
rem  pages, none of your details, and none of your website's history.
rem  Just double-click this file. There is nothing to type.
rem ===================================================================
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Make a kit to give away

set "OUTNAME=website-kit"
set "MISSING="

rem -------------------------------------------------------------------
rem  The kit is an exact list of files. Nothing outside this list is
rem  ever copied, so nothing of yours can travel with it by accident.
rem -------------------------------------------------------------------
set "F1=.gitignore"
set "F2=PUBLISH.bat"
set "F3=MAKE-KIT.bat"
set "F4=START-HERE.md"
set "F5=my-github-details.EXAMPLE.txt"
set "F6=scripts\build_index.py"
set "F7=.github\workflows\deploy.yml"

echo.
echo  =====================================================
echo    MAKING A CLEAN KIT TO GIVE AWAY
echo  =====================================================
echo.

for %%N in ("%F1%" "%F2%" "%F3%" "%F4%" "%F5%" "%F6%" "%F7%") do (
  if not exist "%%~N" set "MISSING=%%~N"
)
if defined MISSING goto :err_missing

pushd ".." 2>nul
if errorlevel 1 goto :err_no_parent
set "PARENT=%CD%"
popd

rem -------------------------------------------------------------------
rem  Pick a folder name that is free. An existing folder is never
rem  touched, and neither is this one - we just try the next number.
rem -------------------------------------------------------------------
set "N=1"
:pick_name
set "OUT=%PARENT%\%OUTNAME%"
if not "%N%"=="1" set "OUT=%PARENT%\%OUTNAME%-%N%"
if /i "%OUT%"=="%CD%" goto :next_name
if exist "%OUT%" goto :next_name
goto :name_chosen
:next_name
set /a N+=1
if %N% GTR 20 goto :err_too_many
goto :pick_name
:name_chosen

echo   The new kit is being created here:
echo.
echo     %OUT%
echo.

md "%OUT%" 2>nul
if not exist "%OUT%\" goto :err_make
md "%OUT%\scripts" 2>nul
md "%OUT%\.github\workflows" 2>nul
md "%OUT%\html_files" 2>nul
md "%OUT%\unlisted" 2>nul
if not exist "%OUT%\scripts\" goto :err_make
if not exist "%OUT%\.github\workflows\" goto :err_make
if not exist "%OUT%\html_files\" goto :err_make
if not exist "%OUT%\unlisted\" goto :err_make

for %%N in ("%F1%" "%F2%" "%F3%" "%F4%" "%F5%" "%F6%" "%F7%") do (
  copy /y "%%~N" "%OUT%\%%~N" >nul
  if errorlevel 1 goto :err_copy
)

rem -------------------------------------------------------------------
rem  The two page folders are handed over EMPTY on purpose. Your own
rem  home page is yours, so a fresh kit starts with no pages at all and
rem  builds an automatic "no pages yet" home page on its first publish.
rem  These marker files only keep the empty folders in place.
rem -------------------------------------------------------------------
type nul > "%OUT%\html_files\.gitkeep"
type nul > "%OUT%\unlisted\.gitkeep"
if not exist "%OUT%\html_files\.gitkeep" goto :err_copy
if not exist "%OUT%\unlisted\.gitkeep" goto :err_copy

echo   Done. The new kit holds these nine files and nothing else:
echo.
echo     .gitignore
echo     MAKE-KIT.bat
echo     PUBLISH.bat
echo     START-HERE.md
echo     my-github-details.EXAMPLE.txt
echo     .github\workflows\deploy.yml
echo     html_files\.gitkeep
echo     scripts\build_index.py
echo     unlisted\.gitkeep
echo.
echo   Deliberately NOT copied:
echo     my-github-details.txt - your details file, it holds your token
echo     your own web pages in html_files and unlisted
echo     README.md - it lists YOUR pages; theirs is made on their first publish
echo     the hidden .git folder - your site's history and its address
echo.
echo   Give them that whole folder and tell them to open START-HERE.md.
echo.
goto :finish_ok

rem ===================================================================
rem  Problems
rem ===================================================================

:err_missing
call :problem "A file that belongs to the kit is missing."
echo   I could not find:
echo.
echo     %MISSING%
echo.
echo   Put it back, or get a fresh copy of the kit, then try again.
echo   Nothing was created.
goto :finish_fail

:err_no_parent
call :problem "I cannot look one folder up from here."
echo   Move this folder somewhere simple, such as your Desktop, and
echo   run this again. Nothing was created.
goto :finish_fail

:err_too_many
call :problem "There are already too many kit folders here."
echo   Folders called %OUTNAME%, %OUTNAME%-2 and so on already fill up
echo   the folder next to this one. Delete the ones you no longer need,
echo   then run this again. Nothing was created.
goto :finish_fail

:err_make
call :problem "I could not create the new folder."
echo   The folder next to this one may be read-only, or on a network or
echo   cloud drive. Move this folder to your Desktop and try again.
goto :finish_fail

:err_copy
call :problem "I could not copy one of the files."
echo   A file may be open in another program, or the disk may be full.
echo   Close your editor, delete the half-made folder shown above, and
echo   try again. Do not give that half-made folder to anyone.
goto :finish_fail

:problem
echo.
echo  -----------------------------------------------------
echo    I COULD NOT MAKE THE KIT
echo  -----------------------------------------------------
echo.
echo   %~1
echo.
goto :eof

:finish_ok
echo  Press any key to close this window.
pause >nul
exit /b 0

:finish_fail
echo.
echo  Press any key to close this window.
pause >nul
exit /b 1
