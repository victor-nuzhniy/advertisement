#!/bin/bash
echo "Migrate the database at startup of project."
while ! alembic upgrade head 2>&1; do
  echo "Migration is in progress status."
  sleep 3
done
echo "Create superuser if it had not been created earlier."
while ! python3 -m apps.scripts.admin_user 2>&1; do
  echo "Create initial superuser, if it had not been created earlier."
  sleep 3
done
echo "Docker is fully configured successfully."

exec "$@"
