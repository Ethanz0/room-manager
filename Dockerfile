# Dockerfile
FROM python:3.11-slim

ENV ROLE="ROLE"
ENV SIMULATE_PROD=""

# Install packages needed to build C-based python library mysqlclient
RUN apt-get update && \
    apt-get install -y docker-cli pkg-config libmariadb-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /iot-app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy necessary files
COPY .env .
COPY src ./src

WORKDIR /iot-app/src

# Run the app with its role
CMD python -u start.py --role ${ROLE} ${SIMULATE_PROD}
