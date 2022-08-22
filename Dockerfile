FROM python:latest

WORKDIR /root/ephys-manip-link

COPY requirements.txt .

# App requirements
RUN pip install --no-cache-dir -r requirements.txt

# Dev requirements
RUN pip install --no-cache-dir build twine