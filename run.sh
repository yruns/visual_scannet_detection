#!/bin/bash
set -x

if [ -z "$1" ]; then
    echo "No Specified port, using default port 7005"
    port=7005
else
    port=$1
    echo "User Specified port：$port"
fi

export PYTHONPATH=.

python -u web/app.py --port $port