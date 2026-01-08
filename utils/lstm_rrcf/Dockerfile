FROM arm64v8/python:3.11-slim
COPY utils/lstm_rrcf/requirements.txt ./
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc make procps vim libc6-dev python3-dev libev-dev && \
    pip install -r requirements.txt && \
    apt-get clean
WORKDIR /app
RUN echo "ulimit -n 4096" >> /etc/profile
