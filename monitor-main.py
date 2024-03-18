'''
*Python Script by Jayge91 for monitoring and controlling Daly SMART BMS Devices.*

This script is primarily designed to publish information and control topics over MQTT for use by Home Assistant.

'''


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

# Import other parts:
import bms-mqtt-serial # bring in bms-mqtt-serial.py
import bms-mqtt-mqtt # bring in bms-mqtt-mqtt.py


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

DEVICE = os.environ['DEVICE'] # /dev/ttyS1
MQTT_SERVER = os.environ['MQTT_SERVER'] # core-mosquitto
MQTT_USER = os.environ['MQTT_USER'] # mqtt
MQTT_PASS = os.environ['MQTT_PASS'] # mqtt
MQTT_CLIENT_ID = os.environ['MQTT_CLIENT_ID'] # dalybms
MQTT_DISCOVERY_PREFIX = os.environ['MQTT_DISCOVERY_PREFIX'] # homeassistant
DEVICE_ID = os.environ['DEVICE_ID'] # Daly-Smart-BMS
CELL_COUNT = int(os.environ['CELL_COUNT']) # later won't be needed

print("Environment Variables Imported!")

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


if __name__ == "__main__":
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
    mqtt_state_data_queue = multiprocessing.Queue()


    mqtt_connection_process = multiprocessing.Process(target=mqtt_connection)
    mqtt_data_handling_process = multiprocessing.Process(target=mqtt_data_handling, args=(mqtt_state_data_queue,))

    serial_communication_process = multiprocessing.Process(target=serial_communication, args=(ser, mqtt_data_queue))
    serial_x90_handling_process = multiprocessing.Process(target=serial_x90_handling, args=(serial_x90_queue, mqtt_state_data_queue))
    serial_x92_handling_process = multiprocessing.Process(target=serial_x92_handling, args=(serial_x92_queue, mqtt_state_data_queue))


    send_mqtt_discovery_configs()

    serial_process.start()
    mqtt_connection_process.start()
    mqtt_data_handling_process.start()

    serial_process.join()
    mqtt_connection_process.join()
    mqtt_data_handling_process.join()