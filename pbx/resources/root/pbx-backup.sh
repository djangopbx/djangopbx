#!/bin/sh

export PGPASSWORD="XXXXXXXX"
db_host=127.0.0.1
db_port=5432

now=$(date +%Y-%m-%d)
mkdir -p /var/backups/pbx/postgresql

echo "Backup Started"

#delete postgres backups
find /var/backups/pbx/postgresql/pbx_pgsql* -mtime +4 -exec rm {} \;

#backup the database
pg_dump --verbose -Fc --host=$db_host --port=$db_port -U djangopbx djangopbx --schema=public -f /var/backups/pbx/postgresql/pbx_pgsql_$now.sql

# make a note of the latest backup file name
echo -n "/var/backups/pbx/postgresql/pbx_pgsql_$now.sql" > /var/backups/pbx/postgresql/pbx_pgsql_latest.txt

