# TutorMatch – Peer Tutoring Session Booking and Student Progress Tracking

IT317 Project Development 1: **Account Feature** (Django + PostgreSQL/Supabase).

## Features
- Registration with validation (required fields, valid and unique email, unique username, matching passwords) and hashed passwords
- Login (username or email) and logout (POST), with clear success and error messages
- `@login_required` protection; logged-out users are sent to the login page
- Two roles, **Student** and **Tutor**, each with its own dashboard; opening the other role's URL returns a 403 page
- Profile view and edit (name, email, contact number, bio, photo; tutors also set subjects and rate). Users can only see and edit their own profile
- Landing page with scroll animations, linking to registration by role (`/register/?role=tutor`)

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # macOS/Linux: cp .env.example .env  – then edit the values
```
Create the database (local PostgreSQL), then:
```bash
createdb tutormatch            # or create it in pgAdmin
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```
Open http://127.0.0.1:8000/

### Supabase
Use the values from *Project Settings → Database → Connection info* in `.env` (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`) and set `DB_SSLMODE=require`.

## Tests
```bash
python manage.py test accounts
```
(Tests create their own temporary database, so your PostgreSQL user needs permission to create databases.)

## Structure
```
tutormatch/   settings, urls
accounts/     custom User (role, phone, bio, photo...), forms, views, role decorator, tests
templates/    landing, auth pages, dashboards, profile
static/       css, js, owl mascot images
```

## Git checklist
- Repo name: `TutorMatch-Lastname-Firstname-Section`, set to **Public**
- `.env`, `venv/` and `__pycache__/` are already in `.gitignore`; only `.env.example` is committed
- Commit in small steps, e.g. project setup, User model, register, login/logout, role dashboards, profile, landing page, tests
