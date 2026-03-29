# Deployment Guide

## Production checklist

1. Set environment variables:
   `DEBUG=False`
   `SECRET_KEY=<strong-random-secret>`
   `ALLOWED_HOSTS=<your-domain-or-host>`
   `CSRF_TRUSTED_ORIGINS=https://<your-domain>`
   `DATABASE_URL=<postgres-connection-string>`

2. Optional email setup for password reset:
   `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
   `EMAIL_HOST=<smtp-host>`
   `EMAIL_PORT=587`
   `EMAIL_HOST_USER=<smtp-user>`
   `EMAIL_HOST_PASSWORD=<smtp-password>`
   `EMAIL_USE_TLS=True`

3. For HTTPS deployments also set:
   `SESSION_COOKIE_SECURE=True`
   `CSRF_COOKIE_SECURE=True`
   `SECURE_SSL_REDIRECT=True`

## Render example

- Build command:
  `pip install -r requirements.txt && bash build.sh`

- Start command:
  `gunicorn finance_tracker.wsgi:application`

## Railway example

- Install command:
  `pip install -r requirements.txt`

- Start command:
  `gunicorn finance_tracker.wsgi:application`

- Run once after provisioning:
  `python manage.py migrate`
  `python manage.py createsuperuser`

## Notes

- Static files are served with WhiteNoise in production.
- SQLite works for small demos, but PostgreSQL is recommended for production.
- Password reset email defaults to console output until SMTP settings are configured.
