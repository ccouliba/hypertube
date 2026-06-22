# FROM redis:7-alpine
FROM docker.io/library/redis:7-alpine

WORKDIR /app

EXPOSE 6379
HEALTHCHECK --interval=10s --timeout=5s --retries=5 --start-period=5s \
    CMD redis-cli ping || exit 1

CMD ["redis-server"]