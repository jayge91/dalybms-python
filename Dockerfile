FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY bms-mqtt.py ./
RUN pip install --no-cache-dir -r requirements.txt && mkdir /script

CMD [ "python3", "/script/bms-mqtt.py"]
