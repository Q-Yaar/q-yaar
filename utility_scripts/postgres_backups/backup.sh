#!/bin/bash

# --- Configuration ---
CONTAINER_NAME="docker-db-1"
DB_USER="<DB_USERNAME>"
DB_PASSWORD="<DB_PASSWORD>"
DB_NAME="<DB_NAME>"
BACKUP_DIR="/home/game/postgres_backups"
RETENTION_DAYS=7

# Generate a timestamp for the filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="db_backup_${TIMESTAMP}.dump"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

# --- Execution ---
echo "Starting backup for ${DB_NAME}..."

# Run pg_dump inside the container and route the output to the host file
# We use -F c to create a "custom" format dump, which is compressed and perfect for pg_restore
docker exec -e PGPASSWORD=$DB_PASSWORD $CONTAINER_NAME pg_dump -U $DB_USER -F c $DB_NAME > "$FILEPATH"

if [ $? -eq 0 ]; then
    echo "Backup successful: ${FILEPATH}"
else
    echo "Backup failed!"
    exit 1
fi

# --- Cleanup ---
echo "Removing backups older than ${RETENTION_DAYS} days..."
find $BACKUP_DIR -name "db_backup_*.dump" -type f -mtime +$RETENTION_DAYS -delete

echo "Done."