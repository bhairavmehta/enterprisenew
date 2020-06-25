#!/bin/bash

export PYTHONPATH=$(pwd)/src
export TESTCONFIG=$(pwd)/config.debug.yml

if [ "$(python --version | grep 'Python 3.' > /dev/null && echo 1 || echo 0)" == "0" ]; then
    echo "Please use a virtual env that has Python 3 and above"
fi

pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "Failed to install some requirements."
    exit 1
fi

if [ "$1" == "orch" ] || [ "$1" == "" ]; then
    python $PYTHONPATH/thebox/orchestrator/__main__.py -c $TESTCONFIG
elif [ "$1" == "infer" ]; then
    python $PYTHONPATH/thebox/inference/__main__.py -c $TESTCONFIG
elif [ "$1" == "notif" ]; then
    python $PYTHONPATH/thebox/notification/__main__.py -c $TESTCONFIG
else
    echo "Please specify a valid service name {orch, infer, notif}"
fi
