#!/bin/bash

if [ "$(python --version | grep 'Python 3.' > /dev/null && echo 1 || echo 0)" == "0" ]; then
    echo "Please use a virtual env that has Python 3 and above"
fi

python setup.py bdist_wheel
python setup_orch.py bdist_wheel
python setup_infer.py bdist_wheel
python setup_notif.py bdist_wheel

