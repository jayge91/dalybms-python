# monitor_add_mqtt.py

import serial
import time
import os
import queue
import json
import paho.mqtt.client as mqtt
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Now you can log messages
logger = logging.getLogger(__name__)

## Import Environment Variables:
# Function to check if environment variables are set:
def check_environment_variable(var_name):
    if var_name not in os.environ or not os.environ[var_name]:
        print(f"Error: Environment variable {var_name} is not set or is empty.")
        exit(1)

# Check environment variables:
check_environment_variable('DEVICE')
check_environment_variable('MQTT_SERVER')
check_environment_variable('MQTT_USER')
check_environment_variable('MQTT_PASS')
check_environment_variable('MQTT_CLIENT_ID')
check_environment_variable('MQTT_DISCOVERY_PREFIX')
check_environment_variable('DEVICE_ID')

DEVICE = os.environ['DEVICE'] # /dev/ttyS1
MQTT_SERVER = "core-mosquitto" # os.environ['MQTT_SERVER'] # core-mosquitto
MQTT_USER = os.environ['MQTT_USER'] # mqtt
MQTT_PASS = os.environ['MQTT_PASS'] # mqtt
MQTT_CLIENT_ID = os.environ['MQTT_CLIENT_ID'] # dalybms
MQTT_DISCOVERY_PREFIX = os.environ['MQTT_DISCOVERY_PREFIX'] # homeassistant
DEVICE_ID = os.environ['DEVICE_ID'] # Daly-Smart-BMS


## MQTT:
def mqtt_connection(mqtt_publish_queue):
    logger = logging.getLogger(__name__)
    logger.debug("mqtt_connection process started.")
    # Attempt Connection:
    while True:
        try:
            logger.debug("Connecting to MQTT....")
            logger.debug(" Server: " + os.environ['MQTT_SERVER'])
            client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
            client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
            client.connect(os.environ['MQTT_SERVER'])
            logger.debug("MQTT Connected!")
            # send_mqtt_discovery_configs()
            client.loop_start()
            break # Exit the loop if connection succeeds
        except Exception as e:
            logger.debug("Error connecting to MQTT:", e)
            time.sleep(5) # wait to try again

    # Handle publishing of topics:
    while True:
        try:
            data = mqtt_publish_queue.get(timeout=30) # Pull info from queue
            logger.debug("MQTT Data in Queue:")
            try:
                topic, payload, qos, retain = data
                client.publish(topic, payload, qos=qos, retain=retain)
            except Exception as e:
                logger.debug("Error sending data to MQTT: " + str(e))
        except queue.Empty:
            pass # Queue is empty, continue loop.




## Handle the publishing of states for sensors:
# def mqtt_data_handling(mqtt_state_data_queue):
    # logger = logging.getLogger(__name__)
    # logger.debug("mqtt_data_handling process started.")
    # while True:
        # try:
            # data = mqtt_state_data_queue.get(timeout=5)
            # logger.debug("mqtt_data_handling - Received: " + str(data))
            # for topic, value in data.items():
                # try:
                    # logger.debug("Publishing Data...")
                    # try:
                        # client.publish(topic + '/state', value, 2, False)
                    # except Exception as e:
                        # logger.debug("Error sending state to mqtt: " | str(e))
                    # logger.debug("Data Published on " + str(topic) + "/state")
                # except Exception as e:
                    # logger.debug("Error sending state to mqtt: " + str(e))
        # except queue.Empty:
            # pass # Queue is empty, continue loop



## Publish Discovery Topics:    # client.publish([topic], [data], [qos], [ratain?])
# def publish_mqtt_discovery_config(topic, config):
    # logger = logging.getLogger(__name__)
    # logger.debug("Publishing Discovery: " + str(topic))
    # try:
        # client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
        # client.publish(topic + '/config', config, 2, True)
    # except Exception as e:
        # logger.debug("Error sending config to mqtt: " + str(e))
    

## Function to construct JSON output strings for sensors discovery:
def construct_ha_conf(name, device_class, state_topic, unit_of_measurement, value_template, unique_id, entity_category):
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
        "identifiers": os.environ['DEVICE_ID']
    }
    return ha_conf


## Configure JSON data for Home Assistant Discovery:

# Set Base Topics for Sensors and Control:
MQTT_SENSOR_TOPIC =         os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID'] # "homeassistant/sensor/Daly-Smart-BMS"
MQTT_BINARY_SENSOR_TOPIC =  os.environ['MQTT_DISCOVERY_PREFIX'] + '/binary_sensor/' + os.environ['DEVICE_ID'] # "homeassistant/binary_sensor/Daly-Smart-BMS"
MQTT_SWITCH_TOPIC =         os.environ['MQTT_DISCOVERY_PREFIX'] + '/switch/' + os.environ['DEVICE_ID'] # "homeassistant/switch/Daly-Smart-BMS"


# Status:
STATUS_STATE_TOPIC = MQTT_SENSOR_TOPIC + '_Status_State'
statusStateHaConf =       construct_ha_conf(
    device_class =        None,
    name =                "State",
    state_topic =         STATUS_STATE_TOPIC + '/state',
    unit_of_measurement = None,
    value_template =      "{{ (value) }}", # Static
    unique_id =           DEVICE_ID + '_status_state',
    entity_category =     None
)
STATUS_SOC_TOPIC = MQTT_SENSOR_TOPIC + '_Status_SOC'
statusSocHaConf =         construct_ha_conf(
    device_class =        "battery",
    name =                "SOC",
    state_topic =         STATUS_SOC_TOPIC + '/state',
    unit_of_measurement = "%",
    value_template =      "{{ (value) }}", # Static
    unique_id =           DEVICE_ID + '_status_soc',
    entity_category =     None
)
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
STATUS_HEARTBEAT_TOPIC = MQTT_SENSOR_TOPIC + '_Status_Heartbeat'
statusHeartbeatHaConf =   construct_ha_conf(
    device_class =        None,
    name =                "Heartbeat",
    state_topic =         STATUS_HEARTBEAT_TOPIC + '/state',
    value_template =      "{{ (value) }}",
    unit_of_measurement = None,
    unique_id =           DEVICE_ID + '_status_heartbeat',
    entity_category =     "diagnostic"
)

# Voltage:
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

# Current:
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

# Power:
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


# Temperature:
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

# Switches:
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

def send_mqtt_discovery_configs(mqtt_publish_queue):
    logger = logging.getLogger(__name__)
    logger.debug("Publishing MQTT Discovery Data...")
    mqtt_publish_queue.put((STATUS_STATE_TOPIC + '/config', json.dumps(statusStateHaConf), 2, True))
    mqtt_publish_queue.put((STATUS_SOC_TOPIC + '/config', json.dumps(statusSocHaConf), 2, True))
    mqtt_publish_queue.put((STATUS_CHARGE_MOS_TOPIC + '/config', json.dumps(statusChargeMosHaConf), 2, True))
    mqtt_publish_queue.put((STATUS_DISCHARGE_MOS_TOPIC + '/config', json.dumps(statusDischargeMosHaConf), 2, True))
    mqtt_publish_queue.put((STATUS_CELL_COUNT_TOPIC + '/config', json.dumps(statusCellCountHaConf), 2, True))
    mqtt_publish_queue.put((STATUS_HEARTBEAT_TOPIC + '/config', json.dumps(statusHeartbeatHaConf), 2, True))
    mqtt_publish_queue.put((VOLTAGE_PACK_TOPIC + '/config', json.dumps(voltagePackHaConf), 2, True))
    mqtt_publish_queue.put((VOLTAGE_BALANCE_TOPIC + '/config', json.dumps(voltageBalanceHaConf), 2, True))
    mqtt_publish_queue.put((CURRENT_AMPS_TOPIC + '/config', json.dumps(currentAmpsHaConf), 2, True))
    mqtt_publish_queue.put((CURRENT_AH_REMAINING_TOPIC + '/config', json.dumps(currentAhRemainingHaConf), 2, True))
    mqtt_publish_queue.put((POWER_WATTS_TOPIC + '/config', json.dumps(powerWattsHaConf), 2, True))
    mqtt_publish_queue.put((POWER_KWH_REMAINING_TOPIC + '/config', json.dumps(powerKwhRemainingHaConf), 2, True))
    mqtt_publish_queue.put((TEMPERATURE_BATTERY_TOPIC + '/config', json.dumps(temperatureBatteryHaConf), 2, True))
    mqtt_publish_queue.put((CONTROL_CHARGE_MOS_TOPIC + '/config', json.dumps(controlChargeMosHaConf), 2, True))
    mqtt_publish_queue.put((CONTROL_DISCHARGE_MOS_TOPIC + '/config', json.dumps(controlDischargeMosHaConf), 2, True))