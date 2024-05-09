FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Install OpenJDK-8 and other necessary tools
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk ant ca-certificates-java && \
    apt-get clean && \
    update-ca-certificates -f

# Setup JAVA_HOME -- this is useful for docker commandline and will be available as an env var
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/

COPY . ./
ENV PORT 8080
CMD ["gunicorn", "--bind", ":$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "main:server"]
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:server