FROM python:3.11-slim

ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    postgresql-client \
    libpq-dev \
    libssl-dev \
    libboost-all-dev
    
COPY celery/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/requirements.txt app_requirements.txt
RUN pip install --no-cache-dir -r app_requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir celery[redis]
COPY . /app
RUN addgroup --system hypertube && adduser --system --ingroup hypertube appuser \
    && chown -R appuser:hypertube /app
USER appuser
EXPOSE 5555

CMD ["celery", "-A", "app.tasks.celery:celery_app", "worker", "--beat", "--loglevel=info"]