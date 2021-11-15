#!/bin/bash

pid=$(pgrep -f "python3 start_monitors.py")

if [ $? -eq 0 ]
then
  echo -e "\e[32m●\e[0m" start_monitors.py running as PID $pid
  exit 0
else
  echo -e "\e[31m●\e[0m" "ERROR: monitors not running?"
  exit 1
fi