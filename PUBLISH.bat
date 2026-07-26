@echo off
rem ===================================================================
rem  PUBLISH - puts everything in this folder onto your website.
rem  Just double-click this file. There is nothing to type.
rem ===================================================================
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title Publish my website

set "TEMPLATE_FILE=my-github-details.EXAMPLE.txt"
set "CREDS_FILE="
set "GIT_TERMINAL_PROMPT=0"
set "ERRFILE=%TEMP%\publish-website-error.txt"
set "LISTFILE=%TEMP%\publish-website-list.txt"
call :wipe_temp

echo.
echo  =====================================================
echo    PUBLISHING YOUR WEBSITE
echo  =====================================================
echo.

rem -------------------------------------------------------------------
rem  1. Is Git installed?
rem -------------------------------------------------------------------
git --version >nul 2>&1
if errorlevel 1 goto :err_no_git

rem -------------------------------------------------------------------
rem  2. Find your details file. my-github-details.txt.txt is accepted
rem     too, because Windows hides file endings and that rename slip
rem     is the most common one there is.
rem -------------------------------------------------------------------
if exist "my-github-details.txt" set "CREDS_FILE=my-github-details.txt"
if not defined CREDS_FILE if exist "my-github-details.txt.txt" set "CREDS_FILE=my-github-details.txt.txt"
if not defined CREDS_FILE goto :err_no_details

rem -------------------------------------------------------------------
rem  3. The EXAMPLE file is uploaded to GitHub on purpose, so it must
rem     never hold real details. If its placeholders are gone, someone
rem     filled in the wrong file - stop before the token is published.
rem -------------------------------------------------------------------
if not exist "%TEMPLATE_FILE%" goto :template_ok
findstr /c:"PASTE_YOUR_TOKEN_HERE" "%TEMPLATE_FILE%" >nul 2>&1
if errorlevel 1 goto :err_template_filled
:template_ok

rem -------------------------------------------------------------------
rem  4. Read your four details
rem -------------------------------------------------------------------
set "GITHUB_USERNAME="
set "GITHUB_EMAIL="
set "GITHUB_REPO="
set "GITHUB_TOKEN="
for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%CREDS_FILE%") do (
  if /i "%%A"=="GITHUB_USERNAME" set "GITHUB_USERNAME=%%B"
  if /i "%%A"=="GITHUB_EMAIL" set "GITHUB_EMAIL=%%B"
  if /i "%%A"=="GITHUB_REPO" set "GITHUB_REPO=%%B"
  if /i "%%A"=="GITHUB_TOKEN" set "GITHUB_TOKEN=%%B"
)

call :trim_spaces GITHUB_USERNAME
call :trim_spaces GITHUB_EMAIL
call :trim_spaces GITHUB_REPO
call :trim_spaces GITHUB_TOKEN

set "MISSING_KEY="
if not defined GITHUB_TOKEN set "MISSING_KEY=GITHUB_TOKEN"
if not defined GITHUB_REPO set "MISSING_KEY=GITHUB_REPO"
if not defined GITHUB_EMAIL set "MISSING_KEY=GITHUB_EMAIL"
if not defined GITHUB_USERNAME set "MISSING_KEY=GITHUB_USERNAME"
if defined MISSING_KEY goto :err_missing_value

set "BLANK_KEY="
if "%GITHUB_TOKEN%"=="PASTE_YOUR_TOKEN_HERE" set "BLANK_KEY=GITHUB_TOKEN"
if "%GITHUB_REPO%"=="PASTE_YOUR_REPOSITORY_NAME_HERE" set "BLANK_KEY=GITHUB_REPO"
if "%GITHUB_EMAIL%"=="PASTE_YOUR_GITHUB_EMAIL_HERE" set "BLANK_KEY=GITHUB_EMAIL"
if "%GITHUB_USERNAME%"=="PASTE_YOUR_GITHUB_USERNAME_HERE" set "BLANK_KEY=GITHUB_USERNAME"
if defined BLANK_KEY goto :err_not_filled_in

set "REPO_CHECK=%GITHUB_REPO%"
set "REPO_STRIPPED=%REPO_CHECK:/=%"
if not "%REPO_CHECK%"=="%REPO_STRIPPED%" goto :err_repo_slash
set "REPO_CHECK="
set "REPO_STRIPPED="

rem -------------------------------------------------------------------
rem  5. Work out the addresses. AUTH_URL carries the token and is used
rem     in memory only - it is never written into any file, and it is
rem     never printed.
rem -------------------------------------------------------------------
set "REPO_URL=https://github.com/%GITHUB_USERNAME%/%GITHUB_REPO%.git"
set "AUTH_URL=https://%GITHUB_USERNAME%:%GITHUB_TOKEN%@github.com/%GITHUB_USERNAME%/%GITHUB_REPO%.git"
set "SITE_URL=https://%GITHUB_USERNAME%.github.io/"
if /i not "%GITHUB_REPO%"=="%GITHUB_USERNAME%.github.io" set "SITE_URL=https://%GITHUB_USERNAME%.github.io/%GITHUB_REPO%/"

rem -------------------------------------------------------------------
rem  6. Can we reach the repository? Nothing on this computer has been
rem     touched yet, so everything that fails up to here is harmless.
rem -------------------------------------------------------------------
echo  Checking your GitHub repository...
set "REMOTE_HAS_MAIN="
git -c credential.helper= ls-remote --exit-code --heads "%AUTH_URL%" main >nul 2>"%ERRFILE%"
set "LSREMOTE_RC=%errorlevel%"
if "%LSREMOTE_RC%"=="0" set "REMOTE_HAS_MAIN=1"
if "%LSREMOTE_RC%"=="0" goto :connection_ok
if "%LSREMOTE_RC%"=="2" goto :connection_ok
findstr /i /c:"Could not resolve host" /c:"Failed to connect" /c:"Could not resolve proxy" /c:"timed out" "%ERRFILE%" >nul 2>&1
if not errorlevel 1 goto :err_offline
goto :err_cannot_open_repo
:connection_ok

rem -------------------------------------------------------------------
rem  7. First run in this folder? Set it up.
rem -------------------------------------------------------------------
if exist ".git" goto :repo_ready
echo  Setting up this folder for the first time...
git init -q
if errorlevel 1 goto :err_setup
git symbolic-ref HEAD refs/heads/main
if errorlevel 1 goto :err_setup
:repo_ready
git config user.name "%GITHUB_USERNAME%" >nul 2>&1
git config user.email "%GITHUB_EMAIL%" >nul 2>&1
git remote get-url origin >nul 2>&1
if errorlevel 1 git remote add origin "%REPO_URL%" >nul 2>&1
git remote set-url origin "%REPO_URL%" >nul 2>&1

rem -------------------------------------------------------------------
rem  8. Save a snapshot of this folder FIRST, before fetching anything.
rem     Saving first is deliberate: it keeps the working folder clean,
rem     so the update in step 9 can never half-apply your edits on top
rem     of GitHub's copy and leave a scrambled file behind.
rem -------------------------------------------------------------------
echo  Packing up your files...
git add -A >nul 2>"%ERRFILE%"
if errorlevel 1 goto :err_add

git ls-files > "%LISTFILE%" 2>nul
findstr /i /c:"my-github-details" "%LISTFILE%" | findstr /i /v /c:"my-github-details.EXAMPLE.txt" >nul 2>&1
if not errorlevel 1 goto :err_secret_staged

git diff --cached --quiet
if errorlevel 1 goto :do_commit
set "NOTHING_NEW=1"
echo  Nothing has changed since last time - checking GitHub anyway...
goto :fetch_step
:do_commit
git commit -q -m "Update website" >nul 2>"%ERRFILE%"
if errorlevel 1 goto :err_commit
:fetch_step

rem -------------------------------------------------------------------
rem  9. Collect anything GitHub added since last time - the site build
rem     makes its own commit after every publish - and put your snapshot
rem     on top of it.
rem -------------------------------------------------------------------
if not defined REMOTE_HAS_MAIN goto :merge_done
echo  Getting the latest version from GitHub...
git -c credential.helper= pull --rebase "%AUTH_URL%" main >nul 2>"%ERRFILE%"
if errorlevel 1 goto :pull_broke
git ls-files --unmerged > "%LISTFILE%" 2>nul
for %%S in ("%LISTFILE%") do if not "%%~zS"=="0" goto :pull_broke
:merge_done

rem -------------------------------------------------------------------
rem  10. Send it to GitHub
rem -------------------------------------------------------------------
echo  Sending your website to GitHub...
git -c credential.helper= push "%AUTH_URL%" HEAD:main >nul 2>"%ERRFILE%"
if errorlevel 1 goto :err_push

echo.
echo  =====================================================
echo    DONE - YOUR WEBSITE IS ON ITS WAY
echo  =====================================================
echo.
echo   Everything in this folder has been published.
echo.
echo   Your website:  %SITE_URL%
echo.
echo   GitHub needs about a minute to build the new version.
echo   Make a cup of tea, then refresh the page in your browser.
echo.
goto :finish_ok

rem ===================================================================
rem  Things that can go wrong, in plain English
rem ===================================================================

:err_no_git
call :problem "Git is not installed on this computer."
echo   This kit needs a free program called Git for Windows.
echo.
echo   1. Go to:  https://git-scm.com/download/win
echo   2. Download it and install it. Click Next on every screen.
echo   3. Restart the computer, then double-click PUBLISH again.
goto :finish_fail

:err_no_details
call :problem "I cannot find your details file."
echo   I looked for a file called  my-github-details.txt
echo   in this folder, and it is not there.
echo.
echo   Open  %TEMPLATE_FILE%
echo   and follow the instructions at the top of it. It tells you how
echo   to make your own copy and fill it in.
goto :finish_fail

:err_template_filled
call :problem "You filled in the wrong file."
echo   You typed your details into  %TEMPLATE_FILE%
echo.
echo   That file is uploaded to GitHub, where anyone can read it, so I
echo   stopped before your token could be published.
echo.
echo   Please do this:
echo   1. Open %TEMPLATE_FILE% and put the
echo      PASTE_..._HERE words back where your details are now.
echo   2. Make a COPY of that file, named  my-github-details.txt
echo   3. Put your details in the copy, and save it.
echo.
echo   The copy is the one that stays private on this computer.
goto :finish_fail

:err_missing_value
call :problem "One of your details is missing."
echo   I could not read a value for:  %MISSING_KEY%
echo.
echo   Open  %CREDS_FILE%  and check that line. It has to look
echo   exactly like this, with nothing else on the line:
echo.
echo       %MISSING_KEY%=your value here
echo.
echo   Three things break it, and all three are easy to miss:
echo     * a space in front of the name at the start of the line
echo     * a space on either side of the = sign
echo     * nothing typed after the = sign
goto :finish_fail

:err_not_filled_in
call :problem "You have not filled in all your details yet."
echo   This one still has the example text in it:  %BLANK_KEY%
echo.
echo   Open  %CREDS_FILE%  and replace every PASTE_..._HERE
echo   with your own details, then save the file.
goto :finish_fail

:err_repo_slash
call :problem "Your repository name has a slash in it."
echo   GITHUB_REPO is currently:  %GITHUB_REPO%
echo.
echo   It needs the repository name ONLY, without your account name in
echo   front of it. For a personal website that is your account name
echo   followed by .github.io - for example:
echo.
echo       GITHUB_REPO=%GITHUB_USERNAME%.github.io
goto :finish_fail

:err_setup
call :problem "I could not set this folder up for publishing."
echo   Git is installed, but it would not start a project in this
echo   folder. That usually means the folder is read-only, or it sits
echo   on a network drive or cloud drive that is not available.
echo.
echo   Try moving this folder to your Desktop and running it again.
goto :finish_fail

:err_offline
call :problem "I cannot reach GitHub."
echo   Your computer could not connect to github.com.
echo.
echo   1. Check that you are connected to the internet.
echo   2. Open https://github.com in your browser to make sure.
echo   3. On a work or school network it may simply be blocked.
echo.
echo   Nothing was changed. Just double-click PUBLISH again later.
goto :finish_fail

:err_cannot_open_repo
call :problem "GitHub would not let me open your repository."
echo   I tried to open:
echo       https://github.com/%GITHUB_USERNAME%/%GITHUB_REPO%
echo.
echo   GitHub refused. It is one of these three, most likely first:
echo.
echo   1. Your token is wrong, expired, or was deleted.
echo      Make a new one at  https://github.com/settings/tokens
echo      and put it in %CREDS_FILE% as GITHUB_TOKEN.
echo      Tick BOTH boxes when you make it:  repo  and  workflow.
echo   2. GITHUB_REPO is spelled differently on GitHub. Open the
echo      repository in your browser and compare it letter by letter.
echo   3. GITHUB_USERNAME is spelled differently.
echo.
echo   Nothing on this computer was changed.
goto :finish_fail

:err_add
call :problem "I could not read the files in this folder."
echo   Something here could not be opened. The usual cause is a file
echo   that is still open in another program.
echo.
echo   Close your editor and any open documents, then try again.
goto :finish_fail

:err_secret_staged
call :problem "Your password file was about to be published."
echo   This was about to go to GitHub, and it holds your token:
echo.
findstr /i /c:"my-github-details" "%LISTFILE%" | findstr /i /v /c:"my-github-details.EXAMPLE.txt"
echo.
echo   I stopped before uploading anything.
echo.
echo   This means .gitignore is missing, or its first rule was
echo   changed. Open .gitignore and make sure these two lines are in
echo   it, in this order:
echo.
echo       my-github-details*
echo       !my-github-details.EXAMPLE.txt
echo.
echo   If your token was already uploaded once, delete it at
echo   https://github.com/settings/tokens and make a new one.
goto :finish_fail

:err_commit
call :problem "I could not save a snapshot of your folder."
echo   Git refused to save your changes.
echo.
echo   Check that GITHUB_EMAIL in %CREDS_FILE% is a real
echo   e-mail address, then try again.
goto :finish_fail

:pull_broke
git diff --name-only --diff-filter=U > "%LISTFILE%" 2>nul
git rebase --abort >nul 2>&1
goto :err_pull

:err_pull
call :problem "GitHub has a version of a file that clashes with yours."
echo   The same file was changed here AND on github.com, in the same
echo   place, so I cannot tell which version you want to keep.
echo.
echo   Nothing was published, and nothing in this folder was lost.
echo.
type "%LISTFILE%" 2>nul
echo.
echo   The usual cause is editing a page on the github.com website as
echo   well as on this computer. To fix it: open that page on
echo   github.com, copy the part you want to keep into the same file
echo   in this folder, save it, and double-click PUBLISH again.
echo.
echo   If this is your very first publish, the cause is different: the
echo   repository was created with a file already in it. Make a new,
echo   completely empty repository on GitHub - do not tick "Add a
echo   README file" - and run PUBLISH again.
goto :finish_fail

:err_push
findstr /i /c:"Could not resolve host" /c:"Failed to connect" /c:"timed out" "%ERRFILE%" >nul 2>&1
if not errorlevel 1 goto :err_offline
findstr /i /c:"non-fast-forward" /c:"fetch first" /c:"rejected" "%ERRFILE%" >nul 2>&1
if not errorlevel 1 goto :err_push_outdated
findstr /i /c:"Invalid username or token" /c:"Authentication failed" /c:"could not read Username" /c:"Permission to" /c:"403" "%ERRFILE%" >nul 2>&1
if not errorlevel 1 goto :err_push_denied
call :problem "GitHub refused the upload."
echo   This is what Git reported:
echo.
findstr /v /c:"%GITHUB_TOKEN%" "%ERRFILE%"
echo.
echo   Nothing was published.
goto :finish_fail

:err_push_denied
call :problem "GitHub would not accept your token."
echo   Your details were refused when I tried to upload.
echo.
echo   Make a new token at  https://github.com/settings/tokens
echo   and tick BOTH boxes:  repo  and  workflow.
echo   A token without the workflow box cannot publish a website.
echo.
echo   Then put the new token in %CREDS_FILE%
echo   as GITHUB_TOKEN and try again.
goto :finish_fail

:err_push_outdated
call :problem "GitHub changed while this was running."
echo   Something updated your repository in the last few seconds.
echo.
echo   Nothing was lost. Just double-click PUBLISH again - it will
echo   collect the newer version first and then publish yours.
goto :finish_fail

rem ===================================================================
rem  Helpers
rem ===================================================================

:problem
echo.
echo  -----------------------------------------------------
echo    I COULD NOT PUBLISH YOUR WEBSITE
echo  -----------------------------------------------------
echo.
echo   %~1
echo.
goto :eof

:trim_spaces
call set "TRIMVAL=%%%~1%%"
:trim_loop
if not defined TRIMVAL goto :trim_done
if not "%TRIMVAL:~-1%"==" " goto :trim_done
set "TRIMVAL=%TRIMVAL:~0,-1%"
goto :trim_loop
:trim_done
set "%~1=%TRIMVAL%"
set "TRIMVAL="
goto :eof

:wipe_temp
if exist "%ERRFILE%" del /q "%ERRFILE%" >nul 2>&1
if exist "%LISTFILE%" del /q "%LISTFILE%" >nul 2>&1
goto :eof

:finish_ok
call :cleanup
echo  Press any key to close this window.
pause >nul
exit /b 0

:finish_fail
echo.
call :cleanup
echo  Press any key to close this window.
pause >nul
exit /b 1

:cleanup
set "GITHUB_TOKEN="
set "AUTH_URL="
call :wipe_temp
goto :eof
