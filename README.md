# Daly Smart BMS Python Script
Python Script that monitors a Daly Smart BMS through UART USB and publishes the data to MQTT. If environment variable is enabled (not yet implemented), MQTT Discovery Topics will be published for HomeAssistant build in, so no need to add the sensors manually to HA.

Feel free to modify anything here to fit your needs, or if you have an improvement, I'd be grateful if you submit a PR! (I'm REALLY not super savvy with this stuff and am cobbling together much of what I learned from various places)

Sources for information:
https://github.com/jblance/mpp-solar/blob/master/docs/protocols/DALY-Daly_RS485_UART_Protocol.pdf
https://diysolarforum.com/threads/decoding-the-daly-smartbms-protocol.21898/



## Install
[Will eventually be published to docker hub]
Build from dockerfile and utilize .env file for script system variables

Place only *ONE* script in the /script/ folder (map host path/volume to /script and add the file. It will automatically be run on container start.)
Note: I don't know if this can handle multiple scripts?

ENV entries:
(placeholder)
