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
check_environment_variable('DEVICE')
check_environment_variable('MQTT_SERVER')
check_environment_variable('MQTT_USER')
check_environment_variable('MQTT_PASS')
check_environment_variable('MQTT_CLIENT_ID')
check_environment_variable('MQTT_DISCOVERY_PREFIX')
check_environment_variable('DEVICE_ID')
check_environment_variable('CELL_COUNT')

DEVICE = os.environ['DEVICE'] # /dev/ttyS1
MQTT_SERVER = os.environ['MQTT_SERVER'] # core-mosquitto
MQTT_USER = os.environ['MQTT_USER'] # mqtt
MQTT_PASS = os.environ['MQTT_PASS'] # mqtt
MQTT_CLIENT_ID = os.environ['MQTT_CLIENT_ID'] # dalybms
MQTT_DISCOVERY_PREFIX = os.environ['MQTT_DISCOVERY_PREFIX'] # homeassistant
DEVICE_ID = os.environ['DEVICE_ID'] # Daly-Smart-BMS
# CELL_COUNT = int(os.environ['CELL_COUNT']) # later won't be needed


## Connect to MQTT:
client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
client.connect(os.environ['MQTT_SERVER'])



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Home Assistant Device Discovery:                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

## Set Base Topics for Sensors and Control:
MQTT_BASE_TOPIC = MQTT_DISCOVERY_PREFIX + '/sensor/' + DEVICE_ID # "homeassistant/sensor/Daly-Smart-BMS"
MQTT_SWITCH_TOPIC = MQTT_DISCOVERY_PREFIX + '/switch/' + DEVICE_ID # "homeassistant/sensor/Daly-Smart-BMS"


## Publish Discovery Topics:
# Function to publish MQTT Discovery configurations to Home Assistant:
def publish_mqtt_discovery_config(topic, config):
    client.publish(topic, config, 0, True)

# Function to construct JSON output strings for sensors discovery:
def construct_ha_conf(device_class, name, state_topic, unit_of_measurement, value_template, unique_id, entity_category):
    ha_conf = {} # trying to initialize dictionary
    if device_class:
        ha_conf["device_class"] = device_class
    if name:
        ha_conf["name"] = name
    if state_topic:
        ha_conf["state_topic"] = state_topic
    if unit_of_measurement:
        ha_conf["value_template"] = value_template
    if entity_category:
        ha_conf["entity_category"] = entity_category
        
    ha_conf["device"] = {
        "manufacturer": "Daly Electronics",
        "name": "Daly Smart BMS",
        "identifiers": [DEVICE_ID]
    }
    return ha_conf
    
    
## Configure JSON data for sensors:
# Sensor References:
    # https://developers.home-assistant.io/docs/core/entity/sensor/
    # https://www.home-assistant.io/integrations/sensor/
    # https://www.home-assistant.io/integrations/sensor#device-class
    # https://www.home-assistant.io/integrations/switch/
    
# Status: 

statusState = None
STATUS_STATE_TOPIC =      MQTT_BASE_TOPIC + '/Status/State'
statusStateHaConf =       construct_ha_conf(
    device_class =        None,
    name =                "State",
    state_topic =         STATUS_STATE_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ value }}", # Static
    unique_id =           DEVICE_ID + '_status_state',
    entity_category =     None,
)

statusSoc = None
STATUS_SOC_TOPIC =        MQTT_BASE_TOPIC + '/Status/SOC'
statuSocHaConf =          construct_ha_conf(
    device_class =        "battery",
    name =                "SOC",
    state_topic =         STATUS_SOC_TOPIC + '/state',
    unit_of_measurement = "%",
    value_template =      "{{ value }}", # Static
    unique_id =           DEVICE_ID + '_status_soc',
    entity_category =     None,
)

statusChargeMos = None
STATUS_CHARGE_MOS_TOPIC = MQTT_BASE_TOPIC + '/Status/Charge MOS'
statusChargeMosHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Charge MOS status",
    state_topic =         STATUS_CHARGE_MOS_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_charge_mos',
    entity_category =     "diagnostic"
)

statusChargeMos = None
STATUS_DISCHARGE_MOS_TOPIC = MQTT_BASE_TOPIC + '/Status/Discharge MOS'
statusChargeMosHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Disharge MOS status",
    state_topic =         STATUS_DISCHARGE_MOS_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_discharge_mos',
    entity_category =     "diagnostic"
)

statusCellCount = None
STATUS_CELL_COUNT_TOPIC = MQTT_BASE_TOPIC + '/Status/Cell Count'
statusCellCountHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Disharge MOS status",
    state_topic =         STATUS_DISCHARGE_MOS_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_discharge_mos',
    entity_category =     "diagnostic"
)


statusHeartbeat = None
STATUS_HEARTBEAT_TOPIC =  MQTT_BASE_TOPIC + '/Status/Heartbeat'
statusHeartbeatHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Heartbeat",
    state_topic =         STATUS_HEARTBEAT_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_heartbeat',
    entity_category =     "diagnostic"
)

publish_mqtt_discovery_config(STATUS_STATE_TOPIC + '/config', json.dumps(statusStateHaConf))
publish_mqtt_discovery_config(STATUS_SOC_TOPIC + '/config', json.dumps(statusSocHaConf))
publish_mqtt_discovery_config(STATUS_CHARGE_MOS_TOPIC + '/config', json.dumps(statusChargeMosHaConf))
publish_mqtt_discovery_config(STATUS_DISCHARGE_MOS_TOPIC + '/config', json.dumps(statusDischargeMosHaConf))
publish_mqtt_discovery_config(STATUS_CELL_COUNT_TOPIC + '/config', json.dumps(statusCellCountHaConf))
publish_mqtt_discovery_config(STATUS_HEARTBEAT_TOPIC + '/config', json.dumps(statusHeartbeatMosHaConf))


# Voltage:

voltagePack = None
VOLTAGE_PACK_TOPIC =      MQTT_BASE_TOPIC + '/Voltage/Pack'
voltagePackHaConf =       construct_ha_conf(
    device_class =        "voltage",
    name =                "Battery Pack Voltage",
    state_topic =         VOLTAGE_PACK_TOPIC + '/state',
    unit_of_measurement = "V",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_voltage_pack',
    entity_category =     None,
)

voltageBalance = None
VOLTAGE_BALANCE_TOPIC =   MQTT_BASE_TOPIC + '/Voltage/Balance'
voltageBalanceHaConf =    construct_ha_conf(
    device_class =        "voltage",
    name =                "Balance",
    state_topic =         VOLTAGE_BALANCE_TOPIC + '/state',
    unit_of_measurement = "V",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_voltage_balance',
    entity_category =     "diagnostic"
)

publish_mqtt_discovery_config(VOLTAGE_PACK_TOPIC + '/config', json.dumps(voltagePackHaConf))
publish_mqtt_discovery_config(VOLTAGE_BALANCE_TOPIC + '/config', json.dumps(voltageBalanceHaconf))


# Current:

currentAmps = None
CURRENT_AMPS_TOPIC =      MQTT_BASE_TOPIC + '/Current/Amps'
currentAmpsHaConf =       construct_ha_conf(
    device_class =        "current",
    name =                "Battery Current",
    state_topic =         CURRENT_AMPS_TOPIC + '/state',
    unit_of_measurement = "A",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_current_amps',
    entity_category =     None
)

currentAh = None
CURRENT_AH_REMAINING_TOPIC = MQTT_BASE_TOPIC + '/Current/Ah Remaining'
currentAhRemainingHaConf = construct_ha_conf(
    device_class =        "current",
    name =                "Battery Ah Remaining",
    state_topic =         CURRENT_AH_REMAINING_TOPIC + '/state',
    unit_of_measurement = "A",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_current_ah_remaining',
    entity_category =     "diagnostic"
)

publish_mqtt_discovery_config(CURRENT_AMPS_TOPIC + '/config', json.dumps(currentAmpsHaconf))
publish_mqtt_discovery_config(CURRENT_AH_REMAINING_TOPIC + '/config', json.dumps(currentAhRemainingHaconf))


# Power:

powerWatts = None
POWER_WATTS_TOPIC =       MQTT_BASE_TOPIC + '/Power/Watts'
powerWattsHaConf =        construct_ha_conf(
    device_class =        "power",
    name =                "Battery Watts",
    state_topic =         POWER_WATTS_TOPIC + '/state',
    unit_of_measurement = "W",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_power_watts',
    entity_category =     None
)

powerKwh = None
POWER_KWH_REMAINING_TOPIC = MQTT_BASE_TOPIC + '/Power/KWh Remaining'
powerKwhRemainingHaConf = construct_ha_conf(
    device_class =        "energy_storage",
    name =                "Battery KWh Remaining",
    state_topic =         POWER_KWH_REMAINING_TOPIC + '/state',
    unit_of_measurement = "kWh",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_power_kwh_remaining',
    entity_category =     None
)

publish_mqtt_discovery_config(POWER_WATTS_TOPIC + '/config', json.dumps(powerWattsHaconf))
publish_mqtt_discovery_config(POWER_KWH_REMAINING_TOPIC + '/config', json.dumps(powerKwhRemainingHaConf))


# Temperature:

temperatureBattery = None
TEMPERATURE_BATTERY_TOPIC = MQTT_BASE_TOPIC + '/Temperature/Battery'
temperatureBatteryHaConf = construct_ha_conf(
    device_class =        "temperature",
    name =                "Battery Temperature",
    state_topic =         TEMPERATURE_BATTERY_TOPIC + '/state',
    unit_of_measurement = "°C",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_temperature_battery',
    entity_category =     None
)

publish_mqtt_discovery_config(TEMPERATURE_BATTERY_TOPIC + '/config', json.dumps(temperatureBatteryHaConf))


# Switches:

controlChargeMos = None
CONTROL_CHARGE_MOS_TOPIC = MQTT_SWITCH_TOPIC + '/Control/Charge MOS'
controlChargeMosHaConf = construct_ha_conf(
    device_class =        "switch",
    name =                "Charge MOS",
    state_topic =         CONTROL_CHARGE_MOS_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_control_charge_mos',
    entity_category =     "config"
)

controlDischargeMos = None
CONTROL_DISCHARGE_MOS_TOPIC = MQTT_SWITCH_TOPIC + '/Control/Discharge MOS'
controlDischargeMosHaConf = construct_ha_conf(
    device_class =        "switch",
    name =                "Discharge MOS",
    state_topic =         CONTROL_DISCHARGE_MOS_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_control_discharge_mos',
    entity_category =     "config"
)

publish_mqtt_discovery_config(CONTROL_CHARGE_MOS_TOPIC + '/config', json.dumps(controlChargeMosHaConf))
publish_mqtt_discovery_config(CONTROL_DISCHARGE_MOS_TOPIC + '/config', json.dumps(controlDischargeMosHaConf))



# Variables that are not yet used:
gatherTotalVoltage = None #0x90 - byte 2-3 - Gather total voltage (0.1 V)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Binary Data Handling and Convertion:                                      #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



def cmd(command):
    res = []
    ser.write(command)
    while True:
        s = ser.read(13)
        if (s == b''):
            break
        # print(binascii.hexlify(s, ' '))
        res.append(s)
    return res


def publish(topic, data):
    try:
        client.publish(topic, data, 0, False)
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


def extract_cells_v(buffer):
    return [
        int.from_bytes(buffer[5:7], byteorder='big', signed=False),
        int.from_bytes(buffer[7:9], byteorder='big', signed=False),
        int.from_bytes(buffer[9:11], byteorder='big', signed=False)
    ]





##################################################################
def get_cell_balance(statusCellCount):
    res = cmd(b'\xa5\x40\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\x82')
    if len(res) < 1:
        print('Empty response get_cell_balance')
        return
    cells = []
    for frame in res:
        cells += extract_cells_v(frame)
    cells = cells[:statusCellCount]

    sum = 0
    for i in range(statusCellCount):
        cells[i] = cells[i]/1000
        sum += cells[i]

    ##NEED COMPLETE
    voltageCell1
    voltageCell2
    voltageCell3
    voltageCell4
    voltageCell5
    voltageCell6
    voltageCell7

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

    if currentAmps = -3000:
        currentAmps = 0


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

    json = '{'
    json += '"value":' + str((maxTemp + minTemp) / 2) + ','
    json += '"maxTemp":' + str(maxTemp) + ','
    json += '"maxTempCell":' + str(maxTempCell) + ','
    json += '"minTemp":' + str(minTemp) + ','
    json += '"minTempCell":' + str(minTempCell)
    json += '}'
    # print(json)
    publish(TEMP_TOPIC +'/state', json)

def get_battery_mos_status():
    res = cmd(b'\xa5\x40\x93\x08\x00\x00\x00\x00\x00\x00\x00\x00\x80')
    if len(res) < 1:
        print('Empty response get_battery_mos_status')
        return
    buffer = res[0]
    valueByte = int.from_bytes(buffer[4:5], byteorder='big', signed=False)
    value = 'discharging' if valueByte == 2 else ('charging' if valueByte == 1 else 'idle')
    chargeMOS = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
    dischargeMOS = int.from_bytes(buffer[6:7], byteorder='big', signed=False)
    BMSLife = int.from_bytes(buffer[7:8], byteorder='big', signed=False)
    residualCapacity = int.from_bytes(buffer[8:12], byteorder='big', signed=False)

    # print(json)
    publish(MOS_TOPIC +'/state', json)





while True:
    get_bms_status_info()
    get_battery_state()
    get_cell_balance(statusCellCount)
    get_battery_status()
    get_battery_temp()
    get_battery_mos_status()
    time.sleep(1)
    
ser.close()
print('done')
