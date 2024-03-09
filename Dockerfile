FROM python:3

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir /script && echo "Place your script.py in this folder!" > /script/readme.txt

CMD [ "python", "/script/*.py" ]
