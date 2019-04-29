FROM python:3.7

WORKDIR /app

COPY requirements.txt .
COPY src/             .

RUN pip3 install -r requirements.txt
RUN chmod +x ./run.sh
RUN chmod +x ./create-config.py

ENTRYPOINT ["./run.sh"]
