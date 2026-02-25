#!/bin/bash
# Backup script for LiteLLM proxy database
# Creates timestamped backups of PostgreSQL database

set -e  # Exit on error

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/litellm_backup_${TIMESTAMP}.sql.gz"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ Error: .env file not found!"
    exit 1
fi

echo "🗄️  LiteLLM Proxy - Database Backup"
echo "====================================="
echo ""
echo "Timestamp: $(date)"
echo "Backup file: $BACKUP_FILE"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if containers are running
if ! docker compose ps | grep -q "litellm_postgres.*Up"; then
    echo "❌ Error: PostgreSQL container is not running!"
    echo "Start the services with: docker compose up -d"
    exit 1
fi

echo "Creating backup..."

# Create compressed backup
docker compose exec -T postgres pg_dump \
    -U "${POSTGRES_USER:-litellm_user}" \
    -d "${POSTGRES_DB:-litellm}" \
    --clean \
    --if-exists \
    --verbose \
    2>&1 | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ] && [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo ""
    echo "✅ Backup completed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "File: $BACKUP_FILE"
    echo "Size: $BACKUP_SIZE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # List recent backups
    echo "Recent backups:"
    ls -lht "$BACKUP_DIR" | head -6
    echo ""
    
    # Cleanup old backups (keep last 7 days)
    echo "Cleaning up backups older than 7 days..."
    find "$BACKUP_DIR" -name "litellm_backup_*.sql.gz" -mtime +7 -delete
    echo "✅ Cleanup complete"
    echo ""
    
else
    echo "❌ Backup failed!"
    exit 1
fi

echo "💾 Backup process completed"
