FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install uv

COPY pyproject.toml /app/

RUN uv sync --no-cache

COPY . /app/

EXPOSE 8001
