FROM python:latest

WORKDIR /root/ephys-manip-link

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt