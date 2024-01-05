@echo off
goto:$Main

goto:$Command
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
        if "%MYCOSHIRO_CRITICAL_ERROR%"=="" goto:$RunCommand
        if "%MYCOSHIRO_CRITICAL_ERROR%"=="0" goto:$RunCommand

        :: Hit critical error so skip the command
        echo [ERROR] Critical error detected. Skipped command: !_command!
        set _error_value=%MYCOSHIRO_CRITICAL_ERROR%
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
    endlocal & exit /b
:$Command

:Sudo
    call gsudo status IsElevated --no-output && goto:$IsElevated
    call :Command gsudo cache on
    goto:$IsElevated

    :$IsElevated
    call :Command gsudo %*
exit /b %ERRORLEVEL%

:TrySudo
    call gsudo status IsElevated --no-output && goto:$TryIsElevated
    echo Skipped 'gsudo' as we are not elevated.
    exit /b 0

    :$TryIsElevated
    call :Command gsudo %*
    goto:$TrySudoDone

    :$TrySudoDone
exit /b %ERRORLEVEL%

:Cleanup
    call gsudo status IsElevated --no-output && goto:$CleanupIsElevated
    goto:$CleanupDone

    :$CleanupIsElevated
    call :Command gsudo cache off

    :$CleanupDone
exit /b %ERRORLEVEL%

:$Main
setlocal EnableExtensions
    call :TrySudo py -3 -m pip install --no-warn-script-location --upgrade pip
    if errorlevel 1 goto:$MainError
    call :Command py -3 -m pip install --upgrade --user --no-warn-script-location -r "%~dp0requirements.txt"
    if errorlevel 1 goto:$MainError

    call :Command scoop install pipx
    if errorlevel 1 goto:$MainError
    call :Command scoop update pipx
    if errorlevel 1 goto:$MainError
    call :Command pipx install poetry
    if errorlevel 1 goto:$MainError

    set VIRTUAL_ENV_DISABLE_PROMPT=1
    call :Command poetry shell
    if errorlevel 1 goto:$MainError

    call :Command poetry run pip install --no-warn-script-location --upgrade pip setuptools wheel pytest-github-actions-annotate-failures
    if errorlevel 1 goto:$MainError

    call :Command poetry install --no-interaction --with dev
    if errorlevel 1 goto:$MainError

    call :Command poetry lock
    if errorlevel 1 goto:$MainError

    call :Command poetry run ruff .
    if errorlevel 1 goto:$MainError

    call :Command docker pull "ghcr.io/catthehacker/ubuntu:full-latest"
    call :Command act --pull=false
    :$MainError
        echo [Error] Error during setup. Error level: '%ERRORLEVEL%'
        goto:$MainDone

    :$MainDone
    call :Cleanup
endlocal & exit /b %ERRORLEVEL%
