#!/bin/sh

export PGPASSWORD="XXXXXXXX"
db_host=127.0.0.1
db_port=5432

now=$(date +%Y-%m-%d)
mkdir -p /var/backups/pbx/postgresql

echo "Script exit for safety, edit and remove exit if you really want to run this"
echo "You must also edit the name [DATE] of the backup file"
exit 0

echo "Restore Started"

#remove the old database
psql --host=$db_host --port=$db_port  --username=djangopbx -c 'drop schema public cascade;'
psql --host=$db_host --port=$db_port  --username=djangopbx -c 'create schema public;'

#restore the database
pg_restore -v -Fc --host=$db_host --port=$db_port --dbname=djangopbx --username=djangopbx /var/backups/pbx/postgresql/pbx_pgsql_DATE.sql

