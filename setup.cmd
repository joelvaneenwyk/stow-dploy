@echo off
goto:$Main

:Command
    goto:$CommandVar
    :CommandVar
        setlocal EnableDelayedExpansion
        set "_command=!%~1!"
        set "_command=!_command:      = !"
        set "_command=!_command:    = !"
        set "_command=!_command:   = !"
        set "_command=!_command:  = !"
        set _error_value=0
        if "%CRITICAL_ERROR%"=="" goto:$RunCommand
        if "%CRITICAL_ERROR%"=="0" goto:$RunCommand

        :: Hit critical error so skip the command
        echo [ERROR] Critical error detected. Skipped command: !_command!
        set _error_value=%CRITICAL_ERROR%
        goto:$CommandDone

        :$RunCommand
        echo ##[cmd] !_command!
        call !_command!
        set _error_value=%ERRORLEVEL%

        :$CommandDone
        endlocal & (
            exit /b %_error_value%
        )
    :$CommandVar
setlocal EnableDelayedExpansion
    set "_command=%*"
    call :CommandVar "_command"
endlocal & (
    exit /b %ERRORLEVEL%
)

:Sudo
    call gsudo status IsElevated --no-output && goto:$IsElevated
    call :Command gsudo cache on
    goto:$IsElevated

    :$IsElevated
    call :Command gsudo %*
exit /b %ERRORLEVEL%

:TrySudo
setlocal EnableDelayedExpansion
    set _return_value=0
    call gsudo status IsElevated --no-output && goto:$TryIsElevated
    echo Skipped 'gsudo' as we are not elevated.
    goto:$TrySudoDone

    :$TryIsElevated
    call :Command gsudo %*
    set _return_value=%ERRORLEVEL%
    goto:$TrySudoDone

    :$TrySudoDone
endlocal & exit /b %_return_value%

:ClearError
exit /b 0

:Cleanup
setlocal EnableDelayedExpansion
    set _return_value=0
    call gsudo status IsElevated --no-output && goto:$CleanupIsElevated
    goto:$CleanupDone

    :$CleanupIsElevated
    call :Command gsudo cache off
    set _return_value=%ERRORLEVEL%

    :$CleanupDone
endlocal & exit /b %_return_value%

:InstallPyEnv
    setlocal EnableDelayedExpansion
    if not exist "%~dp0build" mkdir "%~dp0build"
    set "_cmd=Invoke-WebRequest -UseBasicParsing"
    set "_cmd=!_cmd! -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" "
    set "_cmd=!_cmd! -OutFile "%~dp0build\install-pyenv-win.ps1" "
    call :Command pwsh -NoProfile -Command !_cmd!
    call :Command pwsh -NoProfile -File "%~dp0build\install-pyenv-win.ps1"

    where pyenv >nul 2>&1
    if errorlevel 1 goto:$AddPyEnvToPath
    goto:$InstallPyEnvDone

    :$AddPyEnvToPath
    set "PATH=%PATH%;%USERPROFILE%\.pyenv\pyenv-win\bin"
    goto:$InstallPyEnvDone

    :$InstallPyEnvDone
endlocal & (
    set "PATH=%PATH%"
    exit /b %ERRORLEVEL%
)

:PipX
    setlocal EnableDelayedExpansion
    set "_pipx_error_level=0"
    call pipx --version >nul 2>&1
    if errorlevel 1 goto:$InstallPipX
    goto:$FoundPipX

    :$InstallPipX
    if "%PIPX_SETUP%"=="1" goto:$RunPipX
    call :Command scoop install pipx
    if errorlevel 1 goto:$PipXError
    call :Command scoop update pipx
    if errorlevel 1 goto:$PipXError

    :$FoundPipX
    set PIPX_SETUP=1
    goto:$RunPipX

    :$RunPipX
    if exist "%~dp0.venv\Scripts\deactivate.bat" call "%~dp0.venv\Scripts\deactivate.bat"
    :: https://github.com/pypa/pipx/issues/1091
    cd /D "%~dp0"
    call :Command pipx %*
    set "_pipx_error_level=%ERRORLEVEL%"
    goto:$PipXDone

    :$PipXError
    goto:$PipXDone

    :$PipXDone
endlocal & (
    set "PIPX_SETUP=%PIPX_SETUP%"
    exit /b %_pipx_error_level%
)

:Poetry
    setlocal EnableDelayedExpansion
    set "_error_level=0"
    set "_attempted_poetry_install=0"

    ::=====================================
    :: Attempt to run Poetry using global install version and then, as backup, use pipx.
    ::=====================================
    goto:PoetryRunEnd
    :PoetryRun
        call poetry --version >nul 2>&1
        if errorlevel 1 goto:$PoetryRunPipX
        set POETRY_SETUP=1
        call :Command poetry %*
        goto:$PoetryRunDone

        :$PoetryRunPipX
        call :PipX run poetry --version >nul 2>&1
        if errorlevel 1 goto:$PoetryRunMissing
        set POETRY_SETUP=1
        call :PipX run poetry %*
        goto:$PoetryRunDone

        :$PoetryRunMissing
        if "!_attempted_poetry_install!"=="1" goto:$SkipPoetryInstall
        set _attempted_poetry_install=1
        call :PipX install poetry
        goto:PoetryRun

        :$SkipPoetryInstall
        goto:$PoetryRunDone

        :$PoetryRunDone
    exit /b %ERRORLEVEL%
    :PoetryRunEnd

    call :PoetryRun %*
    set "_error_level=%ERRORLEVEL%"
    goto:$PoetryDone

    :$PoetryError
    set "_error_level=%ERRORLEVEL%"
    echo [ERROR] Poetry run failed. Return code: "!_error_level!"
    goto:$PoetryDone

    :$PoetryDone
endlocal & (
    set "POETRY_SETUP=%POETRY_SETUP%"
    exit /b %_error_level%
)

:Python
    setlocal EnableDelayedExpansion
    set VIRTUAL_ENV_DISABLE_PROMPT=1
    if exist "%~dp0.venv\Scripts\activate.bat" call "%~dp0.venv\Scripts\activate.bat"
    cd "%~dp0"
    call :Command py -3 %*
endlocal & exit /b %ERRORLEVEL%

:$Main
setlocal EnableExtensions
    call :ClearError

    if "%~1"=="act" goto:$MainDockerAct
    goto:$MainSetup

    :$MainDockerAct
    call :Command docker pull "ghcr.io/catthehacker/ubuntu:full-latest"
    call :Command act --pull=false
    goto:$MainDone

    :$MainSetup
    call :InstallPyEnv

    call :TrySudo py -3 -m pip install --no-warn-script-location --upgrade pip
    if errorlevel 1 goto:$MainError
    call :Python -m pip install --upgrade --user --no-warn-script-location -r "%~dp0requirements.txt"
    if errorlevel 1 goto:$MainError

    call :Poetry run pip install --no-warn-script-location --upgrade pip setuptools wheel pytest-github-actions-annotate-failures
    if errorlevel 1 goto:$MainError

    call :Poetry install --no-interaction --with dev
    if errorlevel 1 goto:$MainError

    call :Poetry lock
    if errorlevel 1 goto:$MainError

    call :Poetry run ruff .
    if errorlevel 1 goto:$MainError

    echo [INFO] Setup complete for 'stow-dploy' package.
    goto:$MainDone

    ::=====================================
    :: Error handling
    ::=====================================
    :$MainError
        echo [Error] Error during setup. Error level: '%ERRORLEVEL%'
        goto:$MainDone

    :$MainDone
    call :Cleanup
endlocal & (
    set "PATH=%PATH%"
    set "VIRTUAL_ENV_DISABLE_PROMPT=%PATH%"
    exit /b %ERRORLEVEL%
)
