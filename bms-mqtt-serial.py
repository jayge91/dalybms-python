import serial
import time
import os
import queue

# Function for managing serial communication
def serial_communication(ser, serial_x90_queue, serial_x91_queue, serial_x92_queue, serial_x93_queue, serial_x94_queue, serial_x95_queue, serial_x96_queue, serial_x97_queue, serial_x98_queue):
    wait_between_time = 5
    while True:
        # 0x90: SOC, total voltage, current
        x90_command = b'\xa5\x40\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7d'
        print("Command: " + str(x90_command))
        ser.write(x90_command)
        time.sleep(0.1)  # Adjust delay as needed
        x90_response = ser.read(13)
        if x90_response:
            serial_x90_queue.put(x90_response)
            # print("Response: " + str(x90_response))
        else:
            print("No response from device.")
        ser.flushInput()
        time.sleep(wait_between_time)  # Adjust sleep time as needed
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
        time.sleep(wait_between_time)  # Adjust sleep time as needed
        ser.flushInput()
#
#


# Functions for handling serial data responses
#
def serial_x90_handling(serial_x90_queue, mqtt_state_data_queue):
# Set Base Topics for Sensors and Control:
    MQTT_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID'] # "homeassistant/sensor/Daly-Smart-BMS"
    # 0x90: SOC, total voltage, current
    while True:
        try:
            response = serial_x90_queue.get(timeout=5)
            print("0x90 Response: " + str(response))
            # if response = b'xa5\x10\x90\x00\x00\x00\x00\x00\x00\x00\x00\x4d' # add case for when bms is sleeping and responds with all zeros
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
def serial_x92_handling(serial_x92_queue, mqtt_state_data_queue):
    MQTT_SENSOR_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/' + os.environ['DEVICE_ID'] # "homeassistant/sensor/Daly-Smart-BMS"
    # 0x90: SOC, total voltage, current
    while True:
        try:
            response = serial_x92_queue.get(timeout=5)
            print("0x90 Response: " + str(response))
            # if response = b'xa5\x10\x90\x00\x00\x00\x00\x00\x00\x00\x00\x4d' # add case for when bms is sleeping and responds with all zeros
            buffer = response[0]
            
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


def serial_x95_handling(serial_x95_queue, mqtt_state_data_queue):
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
# For the sake of demonstration, let's assume the cell voltages are:
# Frame 1: [3.6, 3.7, 3.8]  (Three cell voltages)
# Frame 2: [3.9, 4.0, 4.1]  (Three cell voltages)
# Frame 3: [4.2]             (One cell voltage)

# Output dictionary representing the parsed cell voltages:
# {
    # 'cell_1_v': 3.6,
    # 'cell_2_v': 3.7,
    # 'cell_3_v': 3.8,
    # 'cell_4_v': 3.9,
    # 'cell_5_v': 4.0,
    # 'cell_6_v': 4.1,
    # 'cell_7_v': 4.2
# }


