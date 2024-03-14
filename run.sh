#!/bin/bash

# Check if bms-mqtt.py is in the /config folder and make a new one if not:
if ! test -f /config/bms-mqtt.py; then
	echo "bms-mqtt.py is not in the /config folder. Creating a copy of the default..."
	echo "Creating '/config/bms-mqtt.py' ...."
	cp /usr/src/app/bms-mqtt.py /config/bms-mqtt.py
	echo "Done."
fi

# Run the python script that monitors the BMS:
python /config/bms-mqtt.py

# Report if the script is exited:  (Should never see this, as the script loops)
echo "Script stopped!"
