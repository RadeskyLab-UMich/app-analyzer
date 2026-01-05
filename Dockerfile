FROM python:3.11-slim-bookworm
COPY requirements.txt ./

# Install dependencies including OpenJDK
RUN apt-get update && \
    # apt-get install -y --no-install-recommends openjdk-11-jre && \
    pip install -r requirements.txt && \
    # Clean up the apt cache to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PORT=8080
COPY . ./
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:server