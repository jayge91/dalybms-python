'''
*Python Script by Jayge91 for monitoring and controlling Daly SMART BMS Devices.*

This script is primarily designed to publish information and control topics over MQTT for use by Home Assistant.

'''

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Now you can log messages
logger = logging.getLogger(__name__)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Initial Setup:                                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

## Import Modules:
print("Importing Modules...")

import json
import serial
import binascii
import time
import os
import paho.mqtt.client as mqtt
import multiprocessing

# Load monitor-mqtt.py:
import monitor_add_mqtt

# Load monitor-serial.py:
import monitor_add_serial


## Import Environment Variables:
print("Importing Environment Variables...")

# Function to check if environment variables are set
def check_environment_variable(var_name):
    if var_name not in os.environ or not os.environ[var_name]:
        print(f"Error: Environment variable {var_name} is not set or is empty.")
        exit(1)

# Check environment variables
print("Checking environment variables are set...")
check_environment_variable('DEVICE')
check_environment_variable('MQTT_SERVER')
check_environment_variable('MQTT_USER')
check_environment_variable('MQTT_PASS')
check_environment_variable('MQTT_CLIENT_ID')
check_environment_variable('MQTT_DISCOVERY_PREFIX')
check_environment_variable('DEVICE_ID')
check_environment_variable('CELL_COUNT')
print("Environment Variables Checked!")


## From siysolarforum.com:
# Command 0xDA appears to address the Charge Control feature with this command switching the MOSFET on
# Code:
# -> A540DA080100000000000000C8
# <- A501DA0801xxxxxxxxxxxxxxyy
# As it seems replies the BMS only with the first byte (0x01) as the following bytes are remains of the previous message.

# To switch the charging MOSFET off again:
# Code:
# -> A540DA080000000000000000C7
# <- A501DA0800xxxxxxxxxxxxxxyy


# Command 0xD9 appears to address the Discharge Control feature with this command switching the MOSFET on
# Code:
# -> A540D9080100000000000000C7
# <- A501D90801xxxxxxxxxxxxxxyy
# As it seems replies the BMS only with the first byte (0x01) as the following bytes are remains of the previous message.

# To switch the charging MOSFET off again:
# Code:
# -> A540D9080000000000000000C6
# <- A501D90800xxxxxxxxxxxxxxyy



print("Connecting to Serial...")
ser = serial.Serial(os.environ['DEVICE'], 9600, timeout=1)
print("Serial Connected.")

serial_x90_queue = multiprocessing.Queue()
serial_x91_queue = multiprocessing.Queue()
serial_x92_queue = multiprocessing.Queue()
serial_x93_queue = multiprocessing.Queue()
serial_x94_queue = multiprocessing.Queue()
serial_x95_queue = multiprocessing.Queue()
serial_x96_queue = multiprocessing.Queue()
serial_x97_queue = multiprocessing.Queue()
serial_x98_queue = multiprocessing.Queue()

mqtt_publish_queue = multiprocessing.Queue()


mqtt_connection_process = multiprocessing.Process(target=monitor_add_mqtt.mqtt_connection, args=(mqtt_publish_queue,))
# mqtt_data_handling_process = multiprocessing.Process(target=monitor_add_mqtt.mqtt_data_handling, args=(mqtt_publish_queue,))

serial_communication_process = multiprocessing.Process(target=monitor_add_serial.serial_communication, args=(ser, serial_x90_queue, serial_x91_queue, serial_x92_queue, serial_x93_queue, serial_x94_queue, serial_x95_queue, serial_x96_queue, serial_x97_queue, serial_x98_queue))
serial_x90_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x90_handling, args=(serial_x90_queue, mqtt_publish_queue))
#(pending) serial_x91_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x91_handling, args=(serial_x91_queue, mqtt_publish_queue))
serial_x92_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x92_handling, args=(serial_x92_queue, mqtt_publish_queue))
serial_x93_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x93_handling, args=(serial_x93_queue, mqtt_publish_queue))
serial_x94_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x94_handling, args=(serial_x94_queue, mqtt_publish_queue))
serial_x95_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x95_handling, args=(serial_x95_queue, mqtt_publish_queue))
#(pending) serial_x96_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x96_handling, args=(serial_x96_queue, mqtt_publish_queue))
#(pending) serial_x97_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x97_handling, args=(serial_x97_queue, mqtt_publish_queue))
#(pending) serial_x98_handling_process = multiprocessing.Process(target=monitor_add_serial.serial_x98_handling, args=(serial_x98_queue, mqtt_publish_queue))

# Start MQTT First:

logger.debug("Starting MQTT Connection Process...")
mqtt_connection_process.start()

# Give MQTT Time to get ready:
# time.sleep(5)
logger.debug("Sending MQTT Discovery Configs")
monitor_add_mqtt.send_mqtt_discovery_configs(mqtt_publish_queue)

# Start
# (remove) mqtt_communication_process.start()
# (remove) mqtt_data_handling_process.start()
serial_communication_process.start()
serial_x90_handling_process.start()
#(pending) serial_x91_handling_process.start()
serial_x92_handling_process.start()
serial_x93_handling_process.start()
serial_x94_handling_process.start()
serial_x95_handling_process.start()


#(pending) serial_x96_handling_process.start()


#(pending) serial_x97_handling_process.start()


#(pending) serial_x98_handling_process.start()


    # serial_communication_process.join()
    # mqtt_connection_process.join()
    # mqtt_data_handling_process.join()
    # serial_x90_handling_process.join()
    # serial_x91_handling_process.join()
    # serial_x92_handling_process.join()
    # serial_x93_handling_process.join()
    # serial_x94_handling_process.join()
    # serial_x95_handling_process.join()
    # #(pending) serial_x96_handling_process.join()
    # #(pending) serial_x97_handling_process.join()
    # #(pending) serial_x98_handling_process.join()


while True:
    time.sleep(0.5)