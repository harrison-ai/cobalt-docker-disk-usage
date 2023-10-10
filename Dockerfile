FROM python:3.11-slim-bookworm

ARG DEBIAN_FRONTEND=noninteractive

COPY ./requirements.txt .

RUN apt-get update && \
    apt-get install -y curl

RUN pip install --no-cache-dir -r requirements.txt

RUN curl -L https://github.com/KSXGitHub/parallel-disk-usage/releases/download/0.9.0/pdu-x86_64-unknown-linux-gnu -o /usr/bin/pdu && \
    chmod +x /usr/bin/pdu

COPY ./app/ /app/

ENTRYPOINT ["python"]
