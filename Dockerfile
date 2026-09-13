FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Pinned: sqlite-web 0.8.1 (manager UI) + gevent 26.8.0 (production WSGI server).
RUN pip install --no-cache-dir \
    "sqlite-web==0.8.1" \
    "gevent==26.8.0"

COPY server.py entrypoint.sh ./

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
