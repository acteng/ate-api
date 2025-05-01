FROM python:3.13-slim

ENV PORT=8000

WORKDIR /usr/src/app
COPY ate_api ./ate_api
COPY pyproject.toml .

RUN pip install --no-cache-dir . \
    && useradd ate-api

USER ate-api

CMD [ "sh", "-c", "uvicorn ate_api.main:app --host 0.0.0.0 --port ${PORT}" ]
