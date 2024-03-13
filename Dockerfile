FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
COPY run.sh /usr/src/app/
COPY bms-mqtt.py /usr/src/app/

RUN chmod +x run.sh \
&& pip install --no-cache-dir -r /usr/src/app/requirements.txt \
&& mkdir /config

CMD /usr/src/app/run.sh
