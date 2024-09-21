#!/bin/bash
nohup ./watcher.sh > watch.log 2>&1 &
PID=$!
echo "PID : $PID"
