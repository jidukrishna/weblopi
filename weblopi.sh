#!/bin/bash

source path/to/pythonenv/bin/activate

sleep 5
cd /path/to/directory/stored
nohup python3 main.py > /dev/null 2>&1 &
nohup python3 api_web.py > /dev/null 2>&1 &
