FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY monitor_main.py ./
COPY monitor_add_mqtt.py ./
COPY monitor_add_serial.py ./

RUN pip install --no-cache-dir -r requirements.txt && mkdir /config
WORKDIR /config

CMD python3 monitor_main.py
