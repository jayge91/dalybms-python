# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Python Script by Jayge91 for monitoring and controlling Daly SMART BMS Devices.                   #
# This script is designed to publish information and control topics over MQTT for Home Assistant.   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Initial Setup:                                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
print("Importing Modules...")

import json
import serial
import binascii
import time
import os
import paho.mqtt.client as mqtt


# Environment Variables:
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
CELL_COUNT = int(os.environ['CELL_COUNT']) # later won't be needed


# Connect to MQTT:
client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
client.connect(os.environ['MQTT_SERVER'])


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Home Assistant Device Discovery:                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

MQTT_BASE_TOPIC = MQTT_DISCOVERY_PREFIX + '/sensor/' + DEVICE_ID # "homeassistant/sensor/Daly-Smart-BMS"

# Function to publish MQTT Discovery configurations to Home Assistant:
def publish_mqtt_discovery_config(topic, config):
    client.publish(topic, config, 0, True)

# Constructing JSON output strings for different sensors discovery:
def construct_ha_conf(device_class, name, state_topic, value_template, unique_id, unit_of_measurement=None, entity_category=None):
    ha_conf = {
        "device_class": device_class,
        "name": name,
        "state_topic": state_topic + '/state',
        "unique_id": unique_id,
        "value_template": value,
    }
    if unit_of_measurement:
        ha_conf["unit_of_measurement"] = unit_of_measurement
    if entity_category:
        ha_conf["entity_category"] = entity_category
    ha_conf["device"] = {
        "manufacturer": "Daly Electronics",
        "name": "Daly Smart BMS",
        "identifiers": [DEVICE_ID]
    }
    return ha_conf
    
    
# Configuring JSON data for different sensors:

STATUS_STATE_TOPIC              = MQTT_BASE_TOPIC + '/Status/State'
stateHaConf = construct_ha_conf(
    device_class                = None,
    name                        = "State",
    state_topic                 = STATUS_STATE_TOPIC + '/state',
    unit_of_measurement         = None,
    value_template              = "{{ value }}", # Static
    unique_id                   = DEVICE_ID + '_status_state',
    entity_category             = None,
)



STATUS_SOC_TOPIC                = MQTT_BASE_TOPIC + '/Status/SOC'
socHaConf = construct_ha_conf(
    device_class                = "battery",
    name                        = "SOC",
    state_topic                 = STATUS_SOC_TOPIC + '/state',
    unit_of_measurement         = "%",
    value_template              = "{{ value }}", # Static
    unique_id                   = DEVICE_ID + '_sensor_soc',
)


publish_mqtt_discovery_config(STATUS_STATE_TOPIC + '/config', json.dumps(stateHaConf))
publish_mqtt_discovery_config(STATUS_SOC_TOPIC + '/config', json.dumps(socHaConf))

### Edited to here ###



voltageHaConf = construct_ha_conf(
    device_class="voltage",
    name="Battery Voltage",
    state_topic=MQTT_DISCOVERY_PREFIX + '/sensor/Voltage/Pack',
    unit_of_measurement="V",
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_voltage'
)

currentHaConf = construct_ha_conf(
    device_class="current",
    name="Battery Current",
    state_topic=CURRENT_TOPIC + '/state',
    unit_of_measurement="A",
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_current'
)

cell1vHaConf = construct_ha_conf(
    device_class="voltage",
    name="Cell Balance",
    state_topic=CELLS_TOPIC + '/state',
    unit_of_measurement="V",
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_balance',
    entity_category="diagnostic"
)

tempHaConf = construct_ha_conf(
    device_class="temperature",
    name="Battery Temperature",
    state_topic=TEMPERATURE_TOPIC + '/state',
    unit_of_measurement="°C",
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_temp',
)

mosHaConf = construct_ha_conf(
    device_class=None,
    name="MOS status",
    state_topic=DIAGNOSTIC_TOPIC + '/state',
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_mos',
    entity_category="diagnostic"
)

chargeMosControlHaConf = construct_ha_conf(
    device_class=None,
    name="Charge MOS Control",
    state_topic=CONTROL_TOPIC + '/Charge MOS Control/state',
    value_template="{{ value_json}}",
    unique_id=DEVICE_ID + '_charge_mos_control',
    entity_category="config"
)

dischargeMosControlHaConf = construct_ha_conf(
    device_class=None,
    name="Discharge MOS Control",
    state_topic=CONTROL_TOPIC + '/Discharge MOS Control/state',
    value_template="{{ value_json.value}}",
    unique_id=DEVICE_ID + '_discharge_mos_control',
    entity_category="config"
)

# Publishing MQTT Discovery configs to Home Assistant
publish_mqtt_discovery_config(STATE_TOPIC + '_soc/config', str(socHaConf))
publish_mqtt_discovery_config(STATE_TOPIC + '_voltage/config', str(voltageHaConf))
publish_mqtt_discovery_config(STATE_TOPIC + '_current/config', str(currentHaConf))
publish_mqtt_discovery_config(TEMPERATURE_TOPIC + '/config', str(tempHaConf))
publish_mqtt_discovery_config(DIAGNOSTIC_TOPIC + '/config', str(mosHaConf))
publish_mqtt_discovery_config(CONTROL_TOPIC + '/charge_mos_control/config', str(chargeMosControlHaConf))
publish_mqtt_discovery_config(CONTROL_TOPIC + '/discharge_mos_control/config', str(dischargeMosControlHaConf))