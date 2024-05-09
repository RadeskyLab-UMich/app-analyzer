FROM python:3.10-slim-buster
COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV PORT 8080
COPY . ./
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:server