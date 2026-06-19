FROM python:3.11-slim

ENV PYTHONPATH=/

WORKDIR /

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    postgresql-client \
    libpq-dev \
    libssl-dev \
    ffmpeg
    
COPY celery/requirements.txt /tmp/celery_requirements.txt
RUN pip install --no-cache-dir -r /tmp/celery_requirements.txt
COPY app/requirements.txt /tmp/app_requirements.txt
RUN pip install --no-cache-dir -r /tmp/app_requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir celery[redis]
COPY app /app
RUN addgroup --system hypertube && adduser --system --ingroup hypertube appuser \
    && chown -R appuser:hypertube /app
USER appuser
EXPOSE 5555

CMD ["celery", "-A", "app.tasks.celery_app:celery_app", "worker", "--beat", "--loglevel=info", "--schedule", "/tmp/celerybeat-schedule"]