# FROM python:3.11
FROM docker.io/library/python:3.11

ENV PYTHONPATH=/
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libboost-all-dev \
    libssl-dev \
    postgresql-client \
    ffmpeg

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
RUN chmod +x /app/entrypoint.sh
RUN addgroup --system hypertube && adduser --system --ingroup hypertube appuser \
    && chown -R appuser:hypertube /app /app/entrypoint.sh
USER appuser
EXPOSE 5000

ENTRYPOINT ["/app/entrypoint.sh"]