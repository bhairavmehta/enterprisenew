@echo off
grep "Python 3." python.version.tmp
REM Check Prereqs
python --version > python.version.tmp 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo Must be using Python 3 to run this
    exit /b 1
)

python setup.py bdist_wheel
python setup_orch.py bdist_wheel
python setup_infer.py bdist_wheel
python setup_notif.py bdist_wheel