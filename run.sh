#!/bin/bash


# Check if bms-mqtt.py is in the /script folder and make a new one if not:
if ! test -f /script/bms-mqtt.py; then
  echo "mbs-mqtt.py is not in the /script folder. Creating a new copy..."
  cp /usr/src/app/bms-mqtt.py /script/bms-mqtt.py
  echo "Done."
fi

# Check if default.env is in the /script folder and make a new one if not:
if ! test -f /script/default.env; then
  echo "mbs-mqtt.py is not in the /script folder. Creating a new copy..."
  cp /usr/src/app/bms-mqtt.py /script/bms-mqtt.py
  echo "Done."
fi

echo "Starting BMS Monitor"
python /script/bms-mqtt.py

echo "Script stopped!"
