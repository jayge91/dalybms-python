#!/bin/bash


# Check if bms-mqtt.py is in the /script folder and make a new one if not:
if ! test -f /dalybms/bms-mqtt.py; then
  echo "bms-mqtt.py is not in the /dalybms folder. Creating a new copy..."
  cp /usr/src/app/bms-mqtt.py /dalybms/bms-mqtt.py
  echo "Done."
fi

# Check if default.env is in the /script folder and make a new one if not:
if ! test -f /dalybms/default.env; then
  echo "default.env is not in the /dalybms folder. Creating a new copy..."
  cp /usr/src/app/bms-mqtt.py /dalybms/bms-mqtt.py
  echo "Done."
fi

echo "Starting BMS Monitor"
python /dalybms/bms-mqtt.py

echo "Script stopped!"
