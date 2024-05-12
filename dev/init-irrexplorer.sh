#!/bin/sh
# This script is responsible for setting up and running the IRRExplorer application.
# 
# It performs the following tasks:
# - Installs the required Python dependencies using Poetry
# - Runs the frontend installation and build commands
# - Runs the database migrations using Alembic
# - Schedules a cron job to periodically import data
# - Starts the IRRExplorer application using the Uvicorn server
# 
# The script should be executed as part of the deployment process for the IRRExplorer application.

pip install --no-cache-dir poetry
poetry install
poetry run frontend-install
poetry run frontend-build
poetry run alembic upgrade head

/bin/echo "0 */3 * * * /usr/local/bin/poetry run import-data >> /var/log/cron.log 2>&1" >/etc/cron.d/poetry_import_data
/bin/echo "" >>/etc/cron.d/poetry_import_data
/bin/chmod 0644 /etc/cron.d/poetry_import_data
/usr/bin/crontab /etc/cron.d/poetry_import_data
/bin/touch /var/log/cron.log
/usr/sbin/service cron start

poetry run import-data&

exec poetry run uvicorn irrexplorer.app:app --host 0.0.0.0 --port 8000 --workers 4 --reload
