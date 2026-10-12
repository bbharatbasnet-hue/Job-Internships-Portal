<<<<<<< HEAD

# BharatCareerHub — Job & Internship Platform

A production-oriented Django recruitment marketplace for job seekers, employers and administrators.

## Run locally

```bash
python -m venv venv
# For Windows Users
venv\Scripts\activate
# For macOS/Linux users
# source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Demo accounts: `demo-employer` / `demo12345` and `demo-seeker` / `demo12345`. These are sample credentials for local/demo use only.

## Main areas

- `/` — professional marketplace homepage
- `/jobs/` — filterable job/internship discovery
- `/companies/` — employer directory
- `/dashboard/` — role-aware workspace
- `/accounts/profile/` — candidate profile and resume
- `/accounts/company/` — employer company profile
- `/notifications/` — notification center
- `/admin/` — Django admin
- `/api/` — REST API

## Production checklist

# Set a unique `SECRET_KEY`, `DEBUG=False`, real `ALLOWED_HOSTS`, HTTPS/CSRF origins, real SMTP credentials via environment variables, PostgreSQL (recommended), object/private media storage, backups, and a real domain. Resume downloads are permission-checked through Django rather than exposing private resume files as public URLs.

# Job-Internships-Portal

> > > > > > > bf388294e0528affaf6cf553180d4ebfe59a8e0b
