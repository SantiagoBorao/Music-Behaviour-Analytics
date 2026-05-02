FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

RUN pip install --no-cache-dir pyspark==3.5.1

WORKDIR /app
COPY solution.py .

CMD ["python", "solution.py"]