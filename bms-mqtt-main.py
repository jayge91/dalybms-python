# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Python Script by Jayge91 for monitoring and controlling Daly SMART BMS Devices.                   #
# This script is designed to publish information and control topics over MQTT for Home Assistant.   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



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


## Connect to MQTT:
print("Connecting to MQTT....")
client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
client.connect(os.environ['MQTT_SERVER'])
print("MQTT Connected!")

## Connect to Serial Port:
print("Connecting to serial...")
ser = serial.Serial(os.environ['DEVICE'], 9600, timeout=1)
print("Serial Connected!")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Home Assistant Device Discovery:                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    










# Variables that are not yet used:
gatherTotalVoltage = None # 0x90 - byte 2-3 - Gather total voltage (0.1 V)

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





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Binary Data Handling and Convertion:                                      #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


# Function to send serial commands to BMS:
def cmd(command):
    print("Serial Command: " + str(command))
    res = []
    ser.write(command)
    while True:
        s = ser.read(13)
        if (s == b''):
            break
        # print(binascii.hexlify(s, ' '))
        res.append(s)
    print("Serial Response: " + str(res))
    return res

# Function to publish MQTT data for sensors:  (under "./state")
def publish(topic, data):
    try:
        client.publish(topic + '/state', data, 0, False)
    except Exception as e:
        print("Error sending to mqtt: " + str(e))


# Function to break down a byte into individual bits:
def get_bit_status(byte):
    bit_status = []
    for i in range(8):  # 8 bits in a byte
        bit_value = (byte >> i) & 0x01
        bit_status.append(bit_value)
    return bit_status

# Example usage:
# byte_value = 170  # Example byte value
# bit_status = get_bit_status(byte_value)
# print(bit_status)  # Output: [0, 1, 0, 1, 0, 1, 0, 1]

# Function to extract the cell voltages from the buffer:
def extract_cells_v(buffer):
    return [
        int.from_bytes(buffer[5:7], byteorder='big', signed=False),
        int.from_bytes(buffer[7:9], byteorder='big', signed=False),
        int.from_bytes(buffer[9:11], byteorder='big', signed=False)
    ]

# Function to get individual cell voltages:
def get_cell_balance(cell_count):
    res = cmd(b'\xa5\x40\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\x82')
    if len(res) < 1:
        print('Empty response get_cell_balance')
        return
    cells = []
    for frame in res:
        cells += extract_cells_v(frame)
    cells = cells[:cell_count]

    sum = 0
    for i in range(cell_count - 1):
        cells[i] = cells[i]/1000
        sum += cells[i]

    ##NEED COMPLETE
    # voltageCell1
    # voltageCell2
    # voltageCell3
    # voltageCell4
    # voltageCell5
    # voltageCell6
    # voltageCell7

def get_battery_state():
    res = cmd(b'\xa5\x40\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7d')
    if len(res) < 1:
        print('Empty response get_battery_state')
        return
    buffer = res[0]
    
    voltagePack = int.from_bytes(buffer[4:6], byteorder='big', signed=False) / 10
    gatherTotalVoltage = int.from_bytes(buffer[6:8], byteorder='big', signed=False) / 10
    currentAmps = int.from_bytes(buffer[8:10], byteorder='big', signed=False) / 10 - 3000
    statusSoc = int.from_bytes(buffer[10:12], byteorder='big', signed=False) / 10

    if currentAmps == -3000:
        currentAmps = 0

    print("voltagePack: " + str(voltagePack))
    publish(VOLTAGE_PACK_TOPIC, voltagePack)
    
    print("gatherTotalVoltage: " + str(gatherTotalVoltage))
    ## Later?
    
    print("currentAmps: " + str(currentAmps))
    publish(CURRENT_AMPS_TOPIC, currentAmps)
    
    print("statusSoc: " + str(statusSoc))
    publish(STATUS_SOC_TOPIC, statusSoc)


def get_battery_status():
    res = cmd(b'\xa5\x40\x94\x08\x00\x00\x00\x00\x00\x00\x00\x00\x81')
    if len(res) < 1:
        print('Empty response get_battery_status')
        return
    buffer = res[0]
    
    statusCellCount = int.from_bytes(buffer[4:5], byteorder='big', signed=False)
    # this temperature seems to always be 1
    temp = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
    charger = 'true' if int.from_bytes(buffer[6:7], byteorder='big', signed=False) == 1 else 'false'
    load = 'true' if int.from_bytes(buffer[7:8], byteorder='big', signed=False) == 1 else 'false'
    # dido = buffer[8:9]
    cycles = int.from_bytes(buffer[9:11], byteorder='big', signed=False)  
    
    
    print("statusCellCount: " + str(statusCellCount))
    publish(STATUS_CELL_COUNT_TOPIC, statusCellCount)
    
    # print("temperatureBattery: " + str(temp))
    # publish(TEMPERATURE_BATTERY_TOPIC + '/state', temperatureBattery)
    
    print("charger: " + str(charger))
    print("load: " + str(load))
    print("cycles: " + str(cycles))


def get_battery_temp():
    res = cmd(b'\xa5\x40\x92\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7f')
    if len(res) < 1:
        print('Empty response get_battery_temp')
        return
    buffer = res[0]
    maxTemp = int.from_bytes(buffer[4:5], byteorder='big', signed=False) - 40
    maxTempCell = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
    minTemp = int.from_bytes(buffer[6:7], byteorder='big', signed=False) - 40
    minTempCell = int.from_bytes(buffer[7:8], byteorder='big', signed=False)

    temperatureBattery = round(((maxTemp + minTemp) / 2), 1)
    print("temperatureBattery: " + str(temperatureBattery))
    publish(TEMPERATURE_BATTERY_TOPIC, temperatureBattery)

def get_battery_mos_status():
    res = cmd(b'\xa5\x40\x93\x08\x00\x00\x00\x00\x00\x00\x00\x00\x80')
    if len(res) < 1:
        print('Empty response get_battery_mos_status')
        return
    buffer = res[0]
    valueByte = int.from_bytes(buffer[4:5], byteorder='big', signed=False)
    
    statusState = 'Discharging' if valueByte == 2 else ('Charging' if valueByte == 1 else 'Idle')
    print("statusState: " + str(statusState))
    publish(STATUS_STATE_TOPIC, statusState)
    
    statusChargeMos = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
    statusChargeMos = 'on' if statusChargeMos == 1 else ('off if statusChargeMos == 0 else 'Unknown')
    print("statusChargeMos: " + str(statusChargeMos))
    publish(STATUS_CHARGE_MOS_TOPIC, statusChargeMos)
    
    statusDischargeMos = int.from_bytes(buffer[6:7], byteorder='big', signed=False)
    statusDischargeMos = 'on' if statusDischargeMos == 1 else ('off' if statusDischargeMos == 0 else 'Unknown')
    print("statusDischargeMos: " + str(statusDischargeMos))
    publish(STATUS_DISCHARGE_MOS_TOPIC, statusDischargeMos)
    
    statusHeartbeat = int.from_bytes(buffer[7:8], byteorder='big', signed=False)
    print("statusHeartbeat: " + str(statusHeartbeat))
    publish(STATUS_HEARTBEAT_TOPIC, statusHeartbeat)
        
    currentAhRemaining = int.from_bytes(buffer[8:12], byteorder='big', signed=False)/1000
    print("currentAhRemaining: " + str(currentAhRemaining))
    publish(CURRENT_AH_REMAINING_TOPIC, currentAhRemaining)

    
    
    
    




while True:
    print("loop_start")
    get_battery_status() # 0x94
    get_battery_state() # 0x90
    get_cell_balance(statusCellCount) # 0x95
    get_battery_temp() # 0x92
    get_battery_mos_status() # 0x93
    # time.sleep(1)
    print("loop_end")
    
ser.close()
print('done')
