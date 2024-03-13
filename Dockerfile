FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY run.sh ./
COPY bms-mqtt.py ./

RUN chmod +x run.sh \
&& pip install --no-cache-dir -r requirements.txt \
&& mkdir /config

CMD cat /bin/bash -c 'source /usr/src/app/run.sh'