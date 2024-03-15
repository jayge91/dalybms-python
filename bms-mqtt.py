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

## Set Base Topics for Sensors and Control:
MQTT_SENSOR_TOPIC = MQTT_DISCOVERY_PREFIX + '/sensor/' + DEVICE_ID # "homeassistant/sensor/Daly-Smart-BMS"
MQTT_BINARY_SENSOR_TOPIC = MQTT_DISCOVERY_PREFIX + '/binary_sensor/' + DEVICE_ID # "homeassistant/switch/Daly-Smart-BMS"
MQTT_SWITCH_TOPIC = MQTT_DISCOVERY_PREFIX + '/switch/' + DEVICE_ID # "homeassistant/switch/Daly-Smart-BMS"


## Publish Discovery Topics:
# Function to publish MQTT Discovery configurations to Home Assistant:
def publish_mqtt_discovery_config(topic, config):
    client.publish(topic, config, 0, True)

# Function to construct JSON output strings for sensors discovery:
def construct_ha_conf(name, device_class, state_topic, unit_of_measurement, value_template, unique_id, entity_category):
    print("Constructing ha_conf for " + name + "...")
    ha_conf = {} # trying to initialize dictionary
    if name:
        ha_conf["name"] = name
    if state_topic:
        ha_conf["state_topic"] = state_topic
    if unit_of_measurement:
        ha_conf["unit_of_measurement"] = unit_of_measurement
    if value_template:
        ha_conf["value_template"] = value_template
    if device_class:
        ha_conf["device_class"] = device_class
    if unique_id:
        ha_conf["unique_id"] = unique_id
    if entity_category:
        ha_conf["entity_category"] = entity_category
        
    ha_conf["device"] = {
        "manufacturer": "Daly Electronics",
        "name": "Daly Smart BMS",
        "identifiers": [DEVICE_ID]
    }
    
    print("done.")
    return ha_conf
    
    
## Configure JSON data for sensors:
# Sensor References:
    # https://developers.home-assistant.io/docs/core/entity/sensor/
    # https://www.home-assistant.io/integrations/sensor/
    # https://www.home-assistant.io/integrations/sensor#device-class
    # https://www.home-assistant.io/integrations/switch/


# Status: 

statusState = 999
STATUS_STATE_TOPIC =      MQTT_SENSOR_TOPIC + '_Status_State'
statusStateHaConf =       construct_ha_conf(
    device_class =        None,
    name =                "State",
    state_topic =         STATUS_STATE_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ (value) }}", # Static
    unique_id =           DEVICE_ID + '_status_state',
    entity_category =     None
)
publish_mqtt_discovery_config(STATUS_STATE_TOPIC + '/config', json.dumps(statusStateHaConf))

statusSoc = 999
STATUS_SOC_TOPIC =        MQTT_SENSOR_TOPIC + '_Status_SOC'
statusSocHaConf =         construct_ha_conf(
    device_class =        "battery",
    name =                "SOC",
    state_topic =         STATUS_SOC_TOPIC + '/state',
    unit_of_measurement = "%",
    value_template =      "{{ (value) }}", # Static
    unique_id =           DEVICE_ID + '_status_soc',
    entity_category =     None
)
publish_mqtt_discovery_config(STATUS_SOC_TOPIC + '/config', json.dumps(statusSocHaConf))

statusChargeMos = ""
STATUS_CHARGE_MOS_TOPIC = MQTT_BINARY_SENSOR_TOPIC + '_Status_Charge_MOS'
statusChargeMosHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Charge MOS status",
    state_topic =         STATUS_CHARGE_MOS_TOPIC + '/state',
    value_template =      "{{ (value) }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_charge_mos',
    entity_category =     "diagnostic"
)
publish_mqtt_discovery_config(STATUS_CHARGE_MOS_TOPIC + '/config', json.dumps(statusChargeMosHaConf))

statusDischargeMos = false
STATUS_DISCHARGE_MOS_TOPIC = MQTT_BINARY_SENSOR_TOPIC + '_Status_Discharge_MOS'
statusDischargeMosHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Disharge MOS status",
    state_topic =         STATUS_DISCHARGE_MOS_TOPIC + '_state',
    value_template =      "{{ (value) }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_discharge_mos',
    entity_category =     "diagnostic"
)
publish_mqtt_discovery_config(STATUS_DISCHARGE_MOS_TOPIC + '/config', json.dumps(statusDischargeMosHaConf))

statusCellCount = 7
STATUS_CELL_COUNT_TOPIC = MQTT_SENSOR_TOPIC + '_Status_Cell_Count'
statusCellCountHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Cell Count",
    state_topic =         STATUS_CELL_COUNT_TOPIC + '/state',
    value_template =      "{{ (value) }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_cell_count',
    entity_category =     "diagnostic"
)
publish_mqtt_discovery_config(STATUS_CELL_COUNT_TOPIC + '/config', json.dumps(statusCellCountHaConf))


statusHeartbeat = 999
STATUS_HEARTBEAT_TOPIC =  MQTT_SENSOR_TOPIC + '_Status_Heartbeat'
statusHeartbeatHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Heartbeat",
    state_topic =         STATUS_HEARTBEAT_TOPIC + '/state',
    value_template =      "{{ (value) }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_heartbeat',
    entity_category =     "diagnostic"
)
publish_mqtt_discovery_config(STATUS_HEARTBEAT_TOPIC + '/config', json.dumps(statusHeartbeatHaConf))


# Voltage:

voltagePack = 999
VOLTAGE_PACK_TOPIC =      MQTT_SENSOR_TOPIC + '_Voltage_Pack'
voltagePackHaConf =       construct_ha_conf(
    device_class =        "voltage",
    name =                "Battery Pack Voltage",
    state_topic =         VOLTAGE_PACK_TOPIC + '/state',
    unit_of_measurement = "V",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_voltage_pack',
    entity_category =     None
)
publish_mqtt_discovery_config(VOLTAGE_PACK_TOPIC + '/config', json.dumps(voltagePackHaConf))

voltageBalance = 999
VOLTAGE_BALANCE_TOPIC =   MQTT_SENSOR_TOPIC + '_Voltage_Balance'
voltageBalanceHaConf =    construct_ha_conf(
    device_class =        "voltage",
    name =                "Balance",
    state_topic =         VOLTAGE_BALANCE_TOPIC + '/state',
    unit_of_measurement = "V",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_voltage_balance',
    entity_category =     "diagnostic"
)
publish_mqtt_discovery_config(VOLTAGE_BALANCE_TOPIC + '/config', json.dumps(voltageBalanceHaConf))


# Current:

currentAmps = 999
CURRENT_AMPS_TOPIC =      MQTT_SENSOR_TOPIC + '_Current_Amps'
currentAmpsHaConf =       construct_ha_conf(
    device_class =        "current",
    name =                "Battery Current",
    state_topic =         CURRENT_AMPS_TOPIC + '/state',
    unit_of_measurement = "A",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_current_amps',
    entity_category =     None
)
publish_mqtt_discovery_config(CURRENT_AMPS_TOPIC + '/config', json.dumps(currentAmpsHaConf))

currentAhRemaining = 999
CURRENT_AH_REMAINING_TOPIC = MQTT_SENSOR_TOPIC + '_Current_Ah_Remaining'
currentAhRemainingHaConf = construct_ha_conf(
    device_class =        "current",
    name =                "Battery Ah Remaining",
    state_topic =         CURRENT_AH_REMAINING_TOPIC + '/state',
    unit_of_measurement = "A",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_current_ah_remaining',
    entity_category =     "diagnostic"
)
publish_mqtt_discovery_config(CURRENT_AH_REMAINING_TOPIC + '/config', json.dumps(currentAhRemainingHaConf))


# Power:

powerWatts = 999
POWER_WATTS_TOPIC =       MQTT_SENSOR_TOPIC + '_Power_Watts'
powerWattsHaConf =        construct_ha_conf(
    device_class =        "power",
    name =                "Battery Watts",
    state_topic =         POWER_WATTS_TOPIC + '/state',
    unit_of_measurement = "W",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_power_watts',
    entity_category =     None
)
publish_mqtt_discovery_config(POWER_WATTS_TOPIC + '/config', json.dumps(powerWattsHaConf))

powerKwh = 999
POWER_KWH_REMAINING_TOPIC = MQTT_SENSOR_TOPIC + '_Power_KWh_Remaining'
powerKwhRemainingHaConf = construct_ha_conf(
    device_class =        "energy_storage",
    name =                "Battery KWh Remaining",
    state_topic =         POWER_KWH_REMAINING_TOPIC + '/state',
    unit_of_measurement = "kWh",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_power_kwh_remaining',
    entity_category =     None
)
publish_mqtt_discovery_config(POWER_KWH_REMAINING_TOPIC + '/config', json.dumps(powerKwhRemainingHaConf))


# Temperature:

temperatureBattery = 999
TEMPERATURE_BATTERY_TOPIC = MQTT_SENSOR_TOPIC + '_Temperature_Battery'
temperatureBatteryHaConf = construct_ha_conf(
    device_class =        "temperature",
    name =                "Battery Temperature",
    state_topic =         TEMPERATURE_BATTERY_TOPIC + '/state',
    unit_of_measurement = "°C",
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_temperature_battery',
    entity_category =     None
)
publish_mqtt_discovery_config(TEMPERATURE_BATTERY_TOPIC + '/config', json.dumps(temperatureBatteryHaConf))


# Switches:

controlChargeMos = 999
CONTROL_CHARGE_MOS_TOPIC = MQTT_SWITCH_TOPIC + '_Control_Charge_MOS'
controlChargeMosHaConf = construct_ha_conf(
    device_class =        "switch",
    name =                "Charge MOS Switch",
    state_topic =         CONTROL_CHARGE_MOS_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_control_charge_mos',
    entity_category =     "configuration"
)
publish_mqtt_discovery_config(CONTROL_CHARGE_MOS_TOPIC + '/config', json.dumps(controlChargeMosHaConf))

controlDischargeMos = 999
CONTROL_DISCHARGE_MOS_TOPIC = MQTT_SWITCH_TOPIC + '_Control_Discharge_MOS'
controlDischargeMosHaConf = construct_ha_conf(
    device_class =        "switch",
    name =                "Discharge MOS Switch",
    state_topic =         CONTROL_DISCHARGE_MOS_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ (value) }}",
    unique_id =           DEVICE_ID + '_control_discharge_mos',
    entity_category =     "configuration"
)
publish_mqtt_discovery_config(CONTROL_DISCHARGE_MOS_TOPIC + '/config', json.dumps(controlDischargeMosHaConf))



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
    res = []
    ser.write(command)
    while True:
        s = ser.read(13)
        if (s == b''):
            break
        # print(binascii.hexlify(s, ' '))
        res.append(s)
    print("Command: " + str(res))
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
