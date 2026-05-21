#!/bin/bash
# Restore script for LiteLLM proxy database
# Restores database from a backup file

set -e  # Exit on error

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found!"
    exit 1
fi

echo "📥 LiteLLM Proxy - Database Restore"
echo "====================================="
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "❌ Error: No backup file specified!"
    echo ""
    echo "Usage: ./scripts/restore.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lt ./backups/*.sql.gz 2>/dev/null || echo "No backups found in ./backups/"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Backup file: $BACKUP_FILE"
echo "Database: ${POSTGRES_DB:-litellm}"
echo ""

# Check if containers are running
if ! docker compose ps | grep -q "litellm_postgres.*Up"; then
    echo "❌ Error: PostgreSQL container is not running!"
    echo "Start the services with: docker compose up -d"
    exit 1
fi

# Confirm restoration
echo "⚠️  WARNING: This will overwrite the current database!"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled."
    exit 0
fi

echo ""
echo "Stopping LiteLLM service..."
docker compose stop litellm

echo "Restoring database..."

# Restore from compressed backup
gunzip -c "$BACKUP_FILE" | docker compose exec -T postgres psql \
    -U "${POSTGRES_USER:-litellm_user}" \
    -d "${POSTGRES_DB:-litellm}"

# Check if restore was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database restored successfully!"
    echo ""
    echo "Starting LiteLLM service..."
    docker compose start litellm
    echo ""
    echo "✅ Restore completed!"
else
    echo "❌ Restore failed!"
    echo "Attempting to start LiteLLM service anyway..."
    docker compose start litellm
    exit 1
fi
