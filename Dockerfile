FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY monitor-main.py ./
COPY monitor-mqtt.py ./
COPY monitor-serial.py ./

RUN pip install --no-cache-dir -r requirements.txt


CMD python3 monitor-main.py
