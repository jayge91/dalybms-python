# bms-mqtt-discovery.py
import os
import json
import paho.mqtt.client as mqtt

# Sensor References:
    # https://developers.home-assistant.io/docs/core/entity/sensor/
    # https://www.home-assistant.io/integrations/sensor/
    # https://www.home-assistant.io/integrations/sensor#device-class
    # https://www.home-assistant.io/integrations/switch/


## Connect to MQTT:
def mqtt_connection():
    while True:
        try:
            print("Connecting to MQTT....")
            client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
            client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
            client.connect(os.environ['MQTT_SERVER'])
            print("MQTT Connected!")
            client.loop_forever()
        except Exception as e:
            print("Error connecting to MQTT:", e)
            time.sleep(5)
            pass


def mqtt_data_handling(mqtt_state_data_queue):
    while True:
        try:
            data = mqtt_state_data_queue.get(timeout=5)
            for topic, value in data.items():
                try:
                    publish_mqtt_sensor_data(topic, value)
                except Exception as e:
                    print("Error sending to mqtt: " + str(e))
        except queue.Empty:
            pass # Queue is empty, continue loop



## Publish Discovery Topics:
# Function to publish MQTT Discovery configurations to Home Assistant:
def publish_mqtt_discovery_config(topic, config):
    # client.publish([topic], [data], [qos], [ratain?])
    client.publish(topic + '/config', config, 0, True)
    
# def publish_mqtt_sensor_data(topic, state):
    # # client.publish([topic], [data], [qos], [ratain?])
    # client.publish(topic + '/state', state, 0, False)



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
        "identifiers": os.environ['DEVICE_ID']
    }
    
    print("done.")
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

def send_mqtt_discovery_configs():
    publish_mqtt_discovery_config( STATUS_STATE_TOPIC, json.dumps(statusStateHaConf))
    publish_mqtt_discovery_config( STATUS_SOC_TOPIC, json.dumps(statusSocHaConf))
    publish_mqtt_discovery_config( STATUS_CHARGE_MOS_TOPIC, json.dumps(statusChargeMosHaConf))
    publish_mqtt_discovery_config( STATUS_DISCHARGE_MOS_TOPIC, json.dumps(statusDischargeMosHaConf))
    publish_mqtt_discovery_config( STATUS_CELL_COUNT_TOPIC, json.dumps(statusCellCountHaConf))
    publish_mqtt_discovery_config( STATUS_HEARTBEAT_TOPIC, json.dumps(statusHeartbeatHaConf))
    publish_mqtt_discovery_config( VOLTAGE_PACK_TOPIC, json.dumps(voltagePackHaConf))
    publish_mqtt_discovery_config( VOLTAGE_BALANCE_TOPIC, json.dumps(voltageBalanceHaConf))
    publish_mqtt_discovery_config( CURRENT_AMPS_TOPIC, json.dumps(currentAmpsHaConf))
    publish_mqtt_discovery_config( CURRENT_AH_REMAINING_TOPIC, json.dumps(currentAhRemainingHaConf))
    publish_mqtt_discovery_config( POWER_WATTS_TOPIC, json.dumps(powerWattsHaConf))
    publish_mqtt_discovery_config( POWER_KWH_REMAINING_TOPIC, json.dumps(powerKwhRemainingHaConf))
    publish_mqtt_discovery_config( TEMPERATURE_BATTERY_TOPIC, json.dumps(temperatureBatteryHaConf))
    publish_mqtt_discovery_config( CONTROL_CHARGE_MOS_TOPIC, json.dumps(controlChargeMosHaConf))
    publish_mqtt_discovery_config( CONTROL_DISCHARGE_MOS_TOPIC, json.dumps(controlDischargeMosHaConf))
    client.publish(topic + '/config', config, 0, True)
