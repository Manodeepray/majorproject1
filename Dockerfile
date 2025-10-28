# Use lightweight Python base
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy files
COPY . .

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip procps && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install ngrok (for exposure)
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc > /dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install -y ngrok && rm -rf /var/lib/apt/lists/*

# Expose both servers
EXPOSE 8000 8001

# Copy your .env (optional)
# COPY .env .env

# Start both uvicorn servers concurrently, plus tests and ngrok
CMD bash -c " \
    source .env 2>/dev/null || true; \
    (uvicorn src.InferenceServer:app --host 0.0.0.0 --port 8000 --reload &) && \
    (uvicorn src.server:app --host 0.0.0.0 --port 8001 --reload &) && \
    sleep 5 && \
    ngrok http 8000 \
"
