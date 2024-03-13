# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Python Script by Jayge91 for monitoring and controlling Daly SMART BMS Devices.
# This script is designed to publish information and control topics over MQTT for Home Assistant.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# MQTT Topic Tree:
	# /MQTT_DISCOVERY_PREFIX
		# /sensor
			# /DEVICE_ID
				# /Status (str: idle, charging, discharging)
					# /Charge MOS # (on/off) (entity_category="diagnostic")
					# /Discharge MOS # (on/off) (entity_category="diagnostic")
					# /Heartbeat # (int) (entity_category="diagnostic")
				# /SOC # (%)
				# /Voltage # (V)
					# /Balance # (V)
					# /Highest Cell # (V)
					# /Lowest Cell # (V)
					# /Cell 1 # (V) (entity_category="diagnostic")
					# /Cell 2 # (V) (entity_category="diagnostic")
					# /Cell 3 # (V) (entity_category="diagnostic")
					# /Cell 4 # (V) (entity_category="diagnostic")
					# /Cell 5 # (V) (entity_category="diagnostic")
					# /Cell 6 # (V) (entity_category="diagnostic")
					# /Cell 7 # (V) (entity_category="diagnostic")
				# /Current # (A)
					# /Ah Remaining # (Ah)
				# /Power # (W)
					# /KWh Remaining # (KWh)
				# /Temperature # (*C)
				# /Control
					# /Charge MOS Control # (on/off) (entity_category="config")
					# /Discharge MOS Control # (on/off) (entity_category="config")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Initial Setup:                                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import serial
import binascii
import time
import os
import paho.mqtt.client as mqtt


# Environment Variables:
MQTT_SERVER = os.environ['MQTT_SERVER'] # ip
MQTT_USER = os.environ['MQTT_USER']
MQTT_PASS = os.environ['MQTT_PASS']
MQTT_CLIENT_ID = os.environ['MQTT_CLIENT_ID']

MQTT_DISCOVERY_PREFIX = os.environ['MQTT_DISCOVERY_PREFIX']
DEVICE_ID = os.environ['DEVICE_ID'] # tty device
CELL_COUNT = int(os.environ['CELL_COUNT']) # later won't be needed


# Connect to MQTT:
client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
client.connect(os.environ['MQTT_SERVER'])


# Define MQTT base topics
BASE_TOPIC = MQTT_DISCOVERY_PREFIX + '/sensor/'
DEVICE_NAME = DEVICE_ID
STATE_TOPIC = BASE_TOPIC + DEVICE_NAME
STATUS_TOPIC = STATE_TOPIC + '/Status'
VOLTAGE_TOPIC = STATE_TOPIC + '/Voltage'
CELLS_TOPIC = VOLTAGE_TOPIC + '/Cells'
BALANCE_TOPIC = VOLTAGE_TOPIC + '/Balance'
CURRENT_TOPIC = STATE_TOPIC + '/Current'
POWER_TOPIC = STATE_TOPIC + '/Power'
TEMPERATURE_TOPIC = STATE_TOPIC + '/Temperature'
DIAGNOSTIC_TOPIC = STATE_TOPIC + '/Diagnostic'
CONTROL_TOPIC = STATE_TOPIC + '/Control'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Home Assistant Device Discovery:                                          #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Function to publish MQTT Discovery configurations to Home Assistant:
def publish_mqtt_discovery_config(topic, config):
    client.publish(topic, config, 0, True)

# Constructing JSON output strings for different sensors discovery:
def construct_ha_conf(device_class, name, state_topic, unit_of_measurement=None, value_template=None, unique_id=None, json_attributes_topic=None, entity_category=None):
    ha_conf = {
        "device_class": device_class,
        "name": name,
        "state_topic": state_topic,
    }
    if unit_of_measurement:
        ha_conf["unit_of_measurement"] = unit_of_measurement
    if value_template:
        ha_conf["value_template"] = value_template
    if unique_id:
        ha_conf["unique_id"] = unique_id
    if json_attributes_topic:
        ha_conf["json_attributes_topic"] = json_attributes_topic
    if entity_category:
        ha_conf["entity_category"] = entity_category
    ha_conf["device"] = {
        "manufacturer": "Daly Electronics",
        "name": "Daly Smart BMS",
        "identifiers": [DEVICE_ID]
    }
    return ha_conf
    
    
# Configuring JSON data for different sensors:
socHaConf = construct_ha_conf(
    device_class="battery",
    name="Battery SOC",
    state_topic=STATE_TOPIC + '/state',
    unit_of_measurement="%",
    value_template="{{ value_json.soc}}",
    unique_id=DEVICE_ID + '_soc',
    json_attributes_topic=STATUS_TOPIC + '/state'
)

voltageHaConf = construct_ha_conf(
    device_class="voltage",
    name="Battery Voltage",
    state_topic=STATE_TOPIC + '/state',
    unit_of_measurement="V",
    value_template="{{ value_json.voltage}}",
    unique_id=DEVICE_ID + '_voltage'
)

currentHaConf = construct_ha_conf(
    device_class="current",
    name="Battery Current",
    state_topic=STATE_TOPIC + '/state',
    unit_of_measurement="A",
    value_template="{{ value_json.current}}",
    unique_id=DEVICE_ID + '_current'
)

cellsHaConf = construct_ha_conf(
    device_class="voltage",
    name="Battery Cell Balance",
    state_topic=CELLS_TOPIC + '/state',
    unit_of_measurement="V",
    value_template="{{ value_json.diff}}",
    unique_id=DEVICE_ID + '_balance',
    json_attributes_topic=CELLS_TOPIC + '/state',
    entity_category="diagnostic"
)

tempHaConf = construct_ha_conf(
    device_class="temperature",
    name="Battery Temperature",
    state_topic=TEMPERATURE_TOPIC + '/state',
    unit_of_measurement="°C",
    value_template="{{ value_json.value}}",
    unique_id=DEVICE_ID + '_temp',
    json_attributes_topic=TEMPERATURE_TOPIC + '/state'
)

mosHaConf = construct_ha_conf(
    device_class=None,
    name="MOS status",
    state_topic=DIAGNOSTIC_TOPIC + '/state',
    value_template="{{ value_json.value}}",
    unique_id=DEVICE_ID + '_mos',
    json_attributes_topic=DIAGNOSTIC_TOPIC + '/state',
    entity_category="diagnostic"
)

chargeMosControlHaConf = construct_ha_conf(
    device_class=None,
    name="Charge MOS Control",
    state_topic=CONTROL_TOPIC + '/Charge MOS Control/state',
    value_template="{{ value_json.value}}",
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
publish_mqtt_discovery_config(CELLS_TOPIC + '/config', str(cellsHaConf))
publish_mqtt_discovery_config(TEMPERATURE_TOPIC + '/config', str(tempHaConf))
publish_mqtt_discovery_config(DIAGNOSTIC_TOPIC + '/config', str(mosHaConf))
publish_mqtt_discovery_config(CONTROL_TOPIC + '/charge_mos_control/config', str(chargeMosControlHaConf))
publish_mqtt_discovery_config(CONTROL_TOPIC + '/discharge_mos_control/config', str(dischargeMosControlHaConf))