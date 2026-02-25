#!/bin/sh

set -e
echo "⏳ Waiting for PostgreSQL to be ready..."

max_attempts=30
attempt=0
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ Database connection failed after $max_attempts attempts"
    exit 1
  fi
  echo "⏳ Waiting for database... ($attempt/$max_attempts)"
  sleep 1
done

echo "✅ Database is ready!"
echo "🔧 Initializing database schema..."
cd /
python -m app.db.init_db

echo "🚀 Starting Flask application..."
exec python -m app.app
