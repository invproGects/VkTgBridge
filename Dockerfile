FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY .env .
COPY ./src/* .

RUN pip install -r requirements.txt