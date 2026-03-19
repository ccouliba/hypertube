#!/bin/sh

set -e
echo "⏳ Waiting for PostgreSQL to be ready..."

max_attempts=30
attempt=0
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ Database connection failed after [$max_attempts] attempts"
    exit 1
  fi
  echo "⏳ Waiting for database... ($attempt/$max_attempts)"
  sleep 1
done

echo "✅ Database is ready!"

export FLASK_APP=app
MIGRATION_DIR="/app/db/migrations"
VERSIONS_DIR="$MIGRATION_DIR/versions"

if [ -d "$VERSIONS_DIR" ] && [ -n "$(ls -A $VERSIONS_DIR 2>/dev/null)" ]; then
  echo "🔧 Applying database migrations..."
  flask db upgrade --directory "$MIGRATION_DIR"
else
  echo "🔧 No migration files found — initializing database schema via create_all..."
  cd /
  python -m app.db.init_db
fi

echo "🚀 Starting Flask application with Gunicorn (factory create_app)..."
cd /
exec gunicorn --bind 0.0.0.0:5000 --workers 4 "app.app:create_app()"
