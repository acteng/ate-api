FROM python:3.13-slim

ENV PORT=8000

WORKDIR /usr/src/app
COPY ate_api ./ate_api
COPY pyproject.toml .

RUN pip install --no-cache-dir . \
    && useradd ate-api

USER ate-api

CMD [ "sh", "-c", "hypercorn ate_api.main:proxy_app --bind 0.0.0.0:${PORT}" ]
