@echo off

SET PYTHONPATH=%cd%\src
SET TESTCONFIG=%cd%\config.debug.yml

REM Check Prereqs
python --version > python.version.tmp 2>&1
grep "Python 3." python.version.tmp
if %ERRORLEVEL% NEQ 0 (
    echo Must be using Python 3 to run this
    exit /b 1
)

REM Install requirements
pip install -r requirements.txt --quiet


SET ORCH=%PYTHONPATH%\thebox\orchestrator\__main__.py
SET INFER=%PYTHONPATH%\thebox\inference\__main__.py
SET NOTIF=%PYTHONPATH%\thebox\notification\__main__.py

if "%1" == "" (
    python %ORCH% -c %TESTCONFIG%
    exit /b 0
)

if "%1" == "orch" (
    python %ORCH% -c %TESTCONFIG%
    exit /b 0
)

if "%1" == "infer" (
    python %INFER% -c %TESTCONFIG%
    exit /b 0
)

if "%1" == "notif" (
    python %NOTIF% -c %TESTCONFIG%
    exit /b 0
)

echo Please supply a valid service name.