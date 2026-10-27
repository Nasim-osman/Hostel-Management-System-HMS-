#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Collecting static assets via WhiteNoise..."
python manage.py collectstatic --no-input

echo "==> Applying database migrations..."
python manage.py migrate

echo "==> Seeding initial HMS demonstration records (Admin, Warden, Accounts, Rooms)..."
python manage.py seed_data

echo "==> Build complete! Starting HMS application..."
