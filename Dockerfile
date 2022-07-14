FROM python:latest

WORKDIR /root/nptraj-sensapex-link

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt