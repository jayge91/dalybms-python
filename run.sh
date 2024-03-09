#!/bin/bash

# Check if bms-mqtt.py is in the /script folder and make a new one if not:
if test -f /script/bms-mqtt.py; then
  echo "bms-mqtt.py exists! Starting BMS Monitor...."
else
  echo "mbs-mqtt.py is not in the /script folder. Creating a new copy..."
  cp /usr/src/app/bms-mqtt.py /script/bms-mqtt.py
  echo "Done. Starting BMS Monitor...."
fi

python3 /script/bms-mqtt.py
