#!/bin/bash

# Check if bms-mqtt.py is in the /config folder and make a new one if not:
if ! test -f /config/bms-mqtt.py; then
  echo "bms-mqtt.py is not in the /config folder. Creating a copy of the default..."
  cp /usr/src/app/bms-mqtt.py /config/bms-mqtt.py
  echo "Done."
fi

python /config/bms-mqtt.py

echo "Script stopped!"
