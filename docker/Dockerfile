FROM python:3.12-slim

RUN pip install uv && \
    uv pip install --system selenium selenium-wire pandas requests sqlalchemy numpy

COPY ./spider.py spider.py
