# Use the OpenJDK image as a parent image
FROM openjdk:8-jre-slim

# Install Python
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PORT 8080
COPY . ./
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app

#FROM python:3.10-slim-buster
#COPY requirements.txt ./
#RUN pip install -r requirements.txt
#
#ENV PORT 8080
#COPY . ./
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:server