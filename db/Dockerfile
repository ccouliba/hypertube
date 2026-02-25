FROM postgres:16-alpine

ENV PYTHONPATH=/app

RUN apk add --no-cache \
    postgresql-contrib \
    postgresql-client

COPY init.sql/ /docker-entrypoint-initdb.d/
RUN mkdir -p /var/lib/postgresql/backups
EXPOSE 5432
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD pg_isready -U postgres || pg_isready -U hypertube
