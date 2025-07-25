#!/bin/bash

echo "====== DEPLOYMENT STARTED ======"

cd /var/www/imaranow || exit

echo "→ Pulling latest code from GitHub..."
git pull origin main

echo "→ Activating virtual environment..."
source venv/bin/activate

echo "→ Installing any new dependencies..."
pip install -r requirements.txt

echo "→ Applying migrations..."
python manage.py migrate --noinput

echo "→ Collecting static files..."
python manage.py collectstatic --noinput

echo "→ Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "====== DEPLOYMENT COMPLETE ======"
