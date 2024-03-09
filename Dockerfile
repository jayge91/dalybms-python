FROM python:3

WORKDIR /usr/src/app

COPY default.env ./
COPY requirements.txt ./
COPY run.sh ./
COPY bms-mqtt.py ./

RUN chmod +x run.sh

RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt upgrade -y

RUN mkdir /dalybms

CMD /bin/bash -c 'printenv'
CMD /bin/bash -c './run.sh'
