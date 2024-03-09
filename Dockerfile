FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY run.sh ./
COPY bms-mqtt.py ./
RUN chmod +x run.sh
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir /script && echo "Place your script.py in this folder!" > /script/readme.txt

CMD /bin/bash -c './run.sh'
