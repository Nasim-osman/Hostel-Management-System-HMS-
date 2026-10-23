# HMS — CI/CD Pipeline & Deployment Guide

## 1. Automated Continuous Integration (GitHub Actions)
The automated CI pipeline is defined in `.github/workflows/ci.yml`. On every `push` and `pull_request` to `master` or `main`, the workflow executes:
1. **Runner Setup:** Spins up `ubuntu-latest` with Python 3.12.
2. **Dependency Cache & Install:** Installs pinned libraries from `requirements.txt`.
3. **Configuration Check:** Copies `.env.example` to `.env`.
4. **Django System Check:** Executes `python manage.py check`.
5. **Migration Drift Detection:** Runs `python manage.py makemigrations --check --dry-run` to detect uncommitted model schema changes.
6. **Automated Test Suite:** Runs `python manage.py test --verbosity=2`.
7. **Administrative Service Validation:** Runs `python manage.py send_reminders` and `python manage.py backup_db`.

---

## 2. Local Development Deployment
```bash
# 1. Clone repository
git clone <repo-url> hms
cd hms

# 2. Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env

# 5. Apply database migrations
python manage.py migrate

# 6. Populate demonstration data
python manage.py seed_data

# 7. Start local development server
python manage.py runserver
```

---

## 3. Production Deployment Topology (WSGI + Nginx + PostgreSQL)
For high-traffic university deployment:
- **Gunicorn WSGI Application Server:**
  ```bash
  gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 4 --timeout 60
  ```
- **Nginx Reverse Proxy:** Serves `/static/` and `/media/` directly from disk with gzip/brotli compression and proxies application requests to port 8000.
- **SSL / TLS Termination:** Enforce HTTPS using Let's Encrypt certificates with HSTS headers.
- **PostgreSQL Configuration:** Update `.env`:
  ```ini
  DATABASE_URL=postgres://hms_user:secure_password@localhost:5432/hms_prod
  USE_SQLITE=False
  DEBUG=False
  ALLOWED_HOSTS=hms.university.edu
  ```

---

## 4. Administrative Backup & Restoration Guide
- **Scheduled Automated Backup:**
  Run via cron at 2:00 AM daily:
  ```bash
  python manage.py backup_db
  ```
- **Restoration Verification:**
  To restore data from an administrative backup snapshot:
  ```bash
  python manage.py loaddata backups/hms_data_dump_<timestamp>.json
  ```
