## 1. Setup the Backup Directory

Create a directory on your host machine to store the backup script and the database dumps:

```bash
mkdir -p ~/postgres_backups
cd ~/postgres_backups

```

## 2. Create the Backup Script

Create a file named `backup.sh`:

```bash
nano backup.sh

```

Paste the following script. **Make sure to update the Configuration section** with your specific database password and confirm the absolute paths.

Refer backup.sh for the script.

```bash
#!/bin/bash

# --- Configuration ---
CONTAINER_NAME="docker-db-1"
DB_USER="<DB_USERNAME>"
DB_PASSWORD="<DB_PASSWORD>"
DB_NAME="<DB_NAME>"
# IMPORTANT: Use the absolute path to your backup directory
BACKUP_DIR="/home/game/postgres_backups"
RETENTION_DAYS=7

# Generate a timestamp for the filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="db_backup_${TIMESTAMP}.dump"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

# --- Execution ---
echo "Starting backup for ${DB_NAME}..."

# Run pg_dump inside the container and route the output to the host file
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

```

## 3. Secure and Make Executable

Since the script contains your plaintext database password, restrict access so only your user can read, write, or execute it:

```bash
chmod 700 backup.sh

```

Test the script manually to ensure it works:

```bash
./backup.sh

```

## 4. Automate with Cron

To automate the backups (e.g., running every day at 2:00 AM), add the script to your crontab:

```bash
crontab -e

```

Add the following line at the bottom. Adjust the paths if your username is different:

```bash
0 2 * * * /home/game/postgres_backups/backup.sh >> /home/game/postgres_backups/backup.log 2>&1

```

## 5. Restoring a Backup

To restore your database from a generated `.dump` file, ensure your Postgres container is running. Use the following command from your host machine, replacing the timestamped filename with the backup you want to restore:

```bash
docker exec -i -e PGPASSWORD="<DB_PASSWORD>" docker-db-1 pg_restore -U <DB_USERNAMW> -d <DB_NAME> --clean --if-exists < /home/game/postgres_backups/db_backup_YYYYMMDD_HHMMSS.dump

```

> **Note:** The `--clean --if-exists` flags will drop existing tables before restoring, ensuring your database perfectly matches the state of the backup.
> """
