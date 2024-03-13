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

# Function to construct JSON output strings for sensors discovery:
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
    
    
## Configuring JSON data for sensors:
# Reference: https://developers.home-assistant.io/docs/core/entity/sensor/
# Status:

STATUS_STATE_TOPIC = MQTT_BASE_TOPIC + '/Status/State'
stateHaConf = construct_ha_conf(
    device_class =        None,
    name =                "State",
    state_topic =         STATUS_STATE_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ value }}", # Static
    unique_id =           DEVICE_ID + '_status_state',
    entity_category =     None,
)

STATUS_SOC_TOPIC = MQTT_BASE_TOPIC + '/Status/SOC'
socHaConf = construct_ha_conf(
    device_class =        "battery",
    name =                "SOC",
    state_topic =         STATUS_SOC_TOPIC + '/state',
    unit_of_measurement = "%",
    value_template =      "{{ value }}", # Static
    unique_id =           DEVICE_ID + '_status_soc',
    entity_category =     None,
)

STATUS_CHARGE_MOS_TOPIC = MQTT_BASE_TOPIC + '/Status/Charge MOS'
chargeMosHaConf = construct_ha_conf(
    device_class =        None,
    name =                "Charge MOS status",
    state_topic =         STATUS_CHARGE_MOS_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + 'status_charge_mos',
    entity_category =     "diagnostic"
)

STATUS_DISCHARGE_MOS_TOPIC = MQTT_BASE_TOPIC + '/Status/Discharge MOS'
chargeMosHaConf = construct_ha_conf(
    device_class =        None,
    name =                "Disharge MOS status",
    state_topic =         STATUS_DISCHARGE_MOS_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + 'status_discharge_mos',
    entity_category =     "diagnostic"
)

STATUS_HEARTBEAT_TOPIC = MQTT_BASE_TOPIC + '/Status/Heartbeat'
heartbeatHaConf = construct_ha_conf(
    device_class =        None,
    name =                "Heartbeat",
    state_topic =         STATUS_HEARTBEAT_TOPIC + '/state',
    value_template =      "{{ value }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_heartbeat',
    entity_category =     "diagnostic"
)

publish_mqtt_discovery_config(STATUS_STATE_TOPIC + '/config', json.dumps(stateHaConf))
publish_mqtt_discovery_config(STATUS_SOC_TOPIC + '/config', json.dumps(socHaConf))
publish_mqtt_discovery_config(STATUS_CHARGE_MOS_TOPIC + '/config', json.dumps(chargeMosHaConf))
publish_mqtt_discovery_config(STATUS_DISCHARGE_MOS_TOPIC + '/config', json.dumps(dischargeMosHaConf))
publish_mqtt_discovery_config(STATUS_HEARTBEAT_TOPIC + '/config', json.dumps(heartbeatMosHaConf))


# Voltage:

VOLTAGE_PACK_TOPIC = MQTT_BASE_TOPIC + '/Status/Heartbeat'
packVoltageHaConf = construct_ha_conf(
    device_class =        "voltage",
    name =                "Battery Pack Voltage",
    state_topic =         VOLTAGE_PACK_TOPIC + '/state',
    unit_of_measurement = "V",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + 'voltage_pack',
    entity_category =     None,
)

VOLTAGE_BALANCE_TOPIC = MQTT_BASE_TOPIC + '/Voltage/Balance'
balanceVoltageHaConf = construct_ha_conf(
    device_class="voltage",
    name="Balance",
    state_topic=VOLTAGE_BALANCE_TOPIC + '/state',
    unit_of_measurement="V",
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_voltage_balance',
    entity_category="diagnostic"
)

publish_mqtt_discovery_config(VOLTAGE_PACK_TOPIC + '/config', json.dumps(packVoltageHaConf))
publish_mqtt_discovery_config(VOLTAGE_BALANCE_TOPIC + '/config', json.dumps(balanceVoltageHaconf))


# Current:

CURRENT_AMPS_TOPIC = MQTT_BASE_TOPIC + '/Current/Amps'
currentAmpsHaConf = construct_ha_conf(
    device_class =        "current",
    name =                "Battery Current",
    state_topic =         CURRENT_AMPS_TOPIC + '/state',
    unit_of_measurement = "A",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_current_amps',
    entity_category =     None
)

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
POWER_WATTS_TOPIC = MQTT_BASE_TOPIC + '/Power/Watts'
powerWattsHaConf = construct_ha_conf(
    device_class =        "power",
    name =                "Battery Watts",
    state_topic =         POWER_WATTS_TOPIC + '/state',
    unit_of_measurement = "W",
    value_template =      "{{ value }}",
    unique_id =           DEVICE_ID + '_power_watts',
    entity_category =     None
)

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


######################
### Edited to here ###
######################


tempHaConf = construct_ha_conf(
    device_class="temperature",
    name="Battery Temperature",
    state_topic=TEMPERATURE_TOPIC + '/state',
    unit_of_measurement="°C",
    value_template="{{ value }}",
    unique_id=DEVICE_ID + '_temp',
)


# Publishing MQTT Discovery configs to Home Assistant
publish_mqtt_discovery_config(STATE_TOPIC + '_soc/config', str(socHaConf))
publish_mqtt_discovery_config(STATE_TOPIC + '_current/config', str(currentHaConf))
publish_mqtt_discovery_config(TEMPERATURE_TOPIC + '/config', str(tempHaConf))
publish_mqtt_discovery_config(DIAGNOSTIC_TOPIC + '/config', str(mosHaConf))
publish_mqtt_discovery_config(CONTROL_TOPIC + '/charge_mos_control/config', str(chargeMosControlHaConf))
publish_mqtt_discovery_config(CONTROL_TOPIC + '/discharge_mos_control/config', str(dischargeMosControlHaConf))
