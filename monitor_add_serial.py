# monitor_add_serial.py


import serial
import time
import os
import queue



## Import Environment Variables:
# Function to check if environment variables are set:
def check_environment_variable(var_name):
    if var_name not in os.environ or not os.environ[var_name]:
        print(f"Error: Environment variable {var_name} is not set or is empty.")
        exit(1)

# Check environment variables:
check_environment_variable('DEVICE')
check_environment_variable('MQTT_DISCOVERY_PREFIX')
check_environment_variable('DEVICE_ID')

DEVICE = os.environ['DEVICE'] # /dev/ttyS1
MQTT_DISCOVERY_PREFIX = os.environ['MQTT_DISCOVERY_PREFIX'] # homeassistant
DEVICE_ID = os.environ['DEVICE_ID'] # Daly-Smart-BMS



################################################
## Function for managing serial communication ##
################################################
#
def serial_communication(ser, serial_x90_queue, serial_x91_queue, serial_x92_queue, serial_x93_queue, serial_x94_queue, serial_x95_queue, serial_x96_queue, serial_x97_queue, serial_x98_queue):
    wait_between_time = 5
    try:
        # 0x90: SOC, total voltage, current
        x90_command = b'\xa5\x40\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7d'
        print("Command: " + str(x90_command))
        ser.write(x90_command)
        time.sleep(0.1)  # Adjust delay as needed
        x90_response = ser.read(13)
        if x90_response:
            serial_x90_queue.put(x90_response)
        else:
            print("No response from device.")
        ser.flushInput()
        time.sleep(wait_between_time)  # Adjust sleep time as needed
#
#
        # 0x91: Maximum & Minimum voltage
#
#
        # 0x92: Maximum & Minimum temperature
        x92_command = b'\xa5\x40\x92\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7f'
        print("Command: " + str(x92_command))
        ser.write(x92_command)
        time.sleep(0.1)  # Adjust delay as needed
        x92_response = ser.read(13)
        if x92_response:
            serial_x92_queue.put(x92_response)
        else:
            print("No response from device.")
        ser.flushInput()
        time.sleep(wait_between_time)  # Adjust sleep time as needed
#        
#
        # 0x93: Charge & Discharge MOS Status, Remaining Ah
#
#
        # 0x94: Status information 1
        x94_command = b'\xa5\x40\x94\x08\x00\x00\x00\x00\x00\x00\x00\x00\x81'
        print("Command: " + str(x94_command))
        ser.write(x94_command)
        time.sleep(0.1)  # Adjust delay as needed
        x94_response = ser.read(13)
        if x94_response:
            serial_x94_queue.put(x94_response)
        else:
            print("No response from device.")
        ser.flushInput()
        time.sleep(wait_between_time)  # Adjust sleep time as needed
#
#
        # 0x95: Cell voltage 1~48
        x95_command = b'\xa5\x40\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\x82'
        print("Command: " + str(x95_command))
        ser.write(x95_command)
        time.sleep(0.1)  # Adjust delay as needed
        while True:
            x95_response = ser.read(13)
            if (x95_response == b''):
                break
            res.append(x95_response)
        if x95_response:
            serial_x95_queue.put(x95_response)
        else:
            print("No response from device.")
        ser.flushInput()
        time.sleep(wait_between_time)  # Adjust sleep time as needed
#
#
        # 0x96: Cell 1~16 Temperature
#
#
        # 0x97: Cell balance State 1~48
#
#
        # 0x98: Battery failure status
        # 0->No error 1->Error
        # Byte 0
        # Bit 0: Cell volt high level 1
        # Bit 1: Cell volt high level 2
        # Bit 2: Cell volt low level 1
        # Bit 3: Cell volt low level 2
        # Bit 4: Sum volt high level 1
        # Bit 5: Sum volt high level 2
        # Bit 6: Sum volt low level 1
        # Bit 7: Sum volt low level 2
        # Byte 1
        # Bit 0: Chg temp high level 1
        # Bit 1: Chg temp high level 2
        # Bit 2: Chg temp low level 1
        # Bit 3: Chg temp low level 2
        # Bit 4: Dischg temp high level 1
        # Bit 5: Dischg temp high level 2
        # Bit 6: Dischg temp low level 1
        # Bit 7: Dischg temp low level 2
        # Byte 2
        # Bit 0: Chg overcurrent level 1
        # Bit 1: Chg overcurrent level 2
        # Bit 2: Dischg overcurrent level 1
        # Bit 3: Dischg overcurrent level 2
        # Bit 4: SOC high level 1
        # Bit 5: SOC high level 2
        # Bit 6: SOC Low level 1
        # Bit 7: SOC Low level 2
        # Byte 3
        # Bit 0: Diff volt level 1
        # Bit 1: Diff volt level 2
        # Bit 2: Diff temp level 1
        # Bit 3: Diff temp level 2
        # Bit 4~Bit7:Reserved
        # Byte 4
        # Bit 0: Chg MOS temp high alarm
        # Bit 1: Dischg MOS temp high alarm
        # Bit 2: Chg MOS temp sensor err
        # Bit 3: Dischg MOS temp sensor err
        # Bit 4: Chg MOS adhesion err
        # Bit 5: Dischg MOS adhesion err
        # Bit 6: Chg MOS open circuit err
        # Bit 7: Discrg MOS open circuit err
        # Byte 5
        # Bit 0: AFE collect chip err
        # Bit 1: Voltage collect dropped
        # Bit 2: Cell temp sensor err
        # Bit 3: EEPROM err
        # Bit 4: RTC err
        # Bit 5: Precharge failure
        # Bit 6: Communication failure
        # Bit 7: Internal communication failure
        # Byte6
        # Bit 0: Current module fault
        # Bit 1: Sum voltage detect fault
        # Bit 2: Short circuit protect fault
        # Bit 3: Low volt forbidden chg fault
        # Bit4-Bit7:Reserved
        # Byte7: Fault code
#
#
    except Exception as e:
        print("An error occurred during serial communication:", e)

##################################################
## Functions for handling serial data responses ##
##################################################
#
def serial_x90_handling(serial_x90_queue, mqtt_state_data_queue):        # 0x90: SOC, total voltage, current

# Set Base Topics for Sensors and Control:
    MQTT_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID'] # "homeassistant/sensor/Daly-Smart-BMS"
    while True:
        try:
            response = serial_x90_queue.get(timeout=5)
            print("0x90 Response: " + str(response))
            buffer = response[0]
            
            pack_voltage = int.from_bytes(buffer[4:6], byteorder='big', signed=False) / 10
            pack_voltage_topic = MQTT_SENSOR_TOPIC + '_Voltage_Pack'
            pack_gather_total_voltage = int.from_bytes(buffer[6:8], byteorder='big', signed=False) / 10
            pack_gather_total_voltage_topic = MQTT_SENSOR_TOPIC + '_Voltage_Pack_gather_total_voltage'
            pack_amps = int.from_bytes(buffer[8:10], byteorder='big', signed=False) / 10 - 3000
            pack_amps_topic = MQTT_SENSOR_TOPIC + '_Current_Pack'
            pack_soc = int.from_bytes(buffer[10:12], byteorder='big', signed=False) / 10
            pack_soc_topic = MQTT_SENSOR_TOPIC + '_Status_SOC'
            
            # pack reports -3000 amps when sleeping, change to 0:
            if pack_amps == -3000:
                pack_amps = 0
            
            print("pack_voltage: " + str(pack_voltage))
            print("pack_gather_total_voltage: " + str(pack_gather_total_voltage))
            print("pack_amps: " + str(pack_amps))
            print("pack_soc: " + str(pack_soc))
            
            mqtt_state_data_queue.put({
                pack_voltage_topic: pack_voltage,
                pack_gather_total_voltage_topic: pack_gather_total_voltage,
                pack_amps_topic: pack_amps,
                pack_soc_topic: pack_soc
            })
        except queue.Empty:
            pass  # Queue is empty, continue loop
#
#
#(pending) def serial_x91_handling(serial_x91_queue, mqtt_state_data_queue):        # 0x91: Maximum & Minimum voltage

#
#
def serial_x92_handling(serial_x92_queue, mqtt_state_data_queue):        # 0x92: Maximum & Minimum temperature
    MQTT_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID'] # "homeassistant/sensor/Daly-Smart-BMS"
    while True:
        try:
            x92_response = serial_x92_queue.get(timeout=5)
            print("0x92 Response: " + str(x92_response))
            buffer = x92_response[0]
            
            maxTemp = int.from_bytes(buffer[4:5], byteorder='big', signed=False) - 40
            maxTempCell = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
            minTemp = int.from_bytes(buffer[6:7], byteorder='big', signed=False) - 40
            minTempCell = int.from_bytes(buffer[7:8], byteorder='big', signed=False)   
            
            pack_temperature = round(((maxTemp + minTemp) / 2), 1)
            pack_temperature_topic = MQTT_SENSOR_TOPIC + '_Temperature_Battery'
            
            print("pack_temperature: " + str(pack_temperature))
            
            mqtt_state_data_queue.put({
                pack_temperature_topic: pack_temperature
            })
        except queue.Empty:
            pass
#
#
#(pending) def serial_x93_handling(serial_x93_queue, mqtt_state_data_queue):        # 0x93: Charge & Discharge MOS Status, Remaining Ah

'''
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
'''
#
#
def serial_x94_handling(serial_x94_queue, mqtt_state_data_queue):        # 0x94: Status information 1
    MQTT_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID'] # "homeassistant/sensor/Daly-Smart-BMS"
    MQTT_BINARY_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/binary_sensor/' + os.environ['DEVICE_ID'] # "homeassistant/binary_sensor/Daly-Smart-BMS"
    # 0x90: SOC, total voltage, current
    while True:
        try:
            x94_response = serial_x94_queue.get(timeout=5)
            print("0x94 Response: " + str(x94_response))
            buffer = x94_response[0]

            cells_count = int.from_bytes(buffer[4:5], byteorder='big', signed=False)
            cells_count_topic = MQTT_SENSOR_TOPIC + '_Status_Cell_Count'
            cycles = int.from_bytes(buffer[9:11], byteorder='big', signed=False)  
            cycles_topic = MQTT_SENSOR_TOPIC + '_Status_Cycles'
            charger = 'true' if int.from_bytes(buffer[6:7], byteorder='big', signed=False) == 1 else 'false'
            charger_topic = MQTT_BINARY_SENSOR_TOPIC + '_Status_Charger'
            load = 'true' if int.from_bytes(buffer[7:8], byteorder='big', signed=False) == 1 else 'false'
            load_topic = MQTT_BINARY_SENSOR_TOPIC + '_Status_Load'
            
            print("cells_count: " + str(cells_count))
            print("cycles: " + str(cycles))
            print("charger: " + str(charger))
            print("load: " + str(load))
            
            mqtt_state_data_queue.put({
                cells_count_topic: cells_count,
                cycles_topic: cycles,
                charger_topic: charger,
                load_topic: load
                
            })
        except queue.Empty:
            pass
#
#
def serial_x95_handling(serial_x95_queue, mqtt_state_data_queue):        # 0x95: Cell voltage 1~48
    MQTT_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID']
    # 0x95: Cell voltage 1~48
    while True:
        try:
            response = serial_x95_queue.get(timeout=5)
            print("0x95 Response: " + str(response))
            cells = []
            current_cell = 0
            for frame in response:
                # Parse cell voltages from each frame
                for i in range(0, len(frame), 13):  # Each frame is 13 bytes
                    cell_voltages = []
                    for j in range(5, 11, 2):  # Cell voltage positions in each frame
                        cell_voltage = int.from_bytes(frame[j:j+2], byteorder='big', signed=False) / 1000
                        if cell_voltage > 0:  # Only add non-zero voltages
                            current_cell += 1
                            cell_variable_name = f'cell_{current_cell}_v'
                            cell_topic = MQTT_SENSOR_TOPIC + f'_Voltage_Cell_{current_cell}'
                            cells.append((cell_topic, cell_voltage))
                            print(f'Cell {current_cell} Voltage: ' + str(cell_voltage))
                        else:
                            break
            mqtt_state_data_queue.put({topic: value for topic, value in cells})
         except queue.Empty:
            pass
#
#
#(pending) def serial_x96_handling(serial_x96_queue, mqtt_state_data_queue):        # 0x96: Cell 1~16 Temperature
#
#
#(pending) def serial_x97_handling(serial_x97_queue, mqtt_state_data_queue):        # 0x97: Cell balance State 1~48
#
#
#(pending) def serial_x98_handling(serial_x98_queue, mqtt_state_data_queue):        # 0x98: Battery failure status
