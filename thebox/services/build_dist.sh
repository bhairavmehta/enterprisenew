#!/bin/bash

if [ "$(python3 --version | grep 'Python 3.' > /dev/null && echo 1 || echo 0)" == "0" ]; then
    echo "Please use a virtual env that has Python 3 and above"
fi

python3 setup.py bdist_wheel
python3 setup_orch.py bdist_wheel
python3 setup_infer.py bdist_wheel
python3 setup_notif.py bdist_wheel

