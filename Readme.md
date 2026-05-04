# TaskFlow — Role-Based Task Management System

A production-ready, full-stack multi-user web application built with Django REST Framework and React. It enables teams to manage tasks across three distinct roles with JWT authentication, asynchronous email notifications, and cloud deployment on Google Cloud Platform.

**Live Application:** [https://taskflow-frontend-834510061034.us-central1.run.app](https://taskflow-frontend-834510061034.us-central1.run.app)

**Backend API:** [https://taskflow-backend-834510061034.us-central1.run.app](https://taskflow-backend-834510061034.us-central1.run.app)

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [User Roles & Permissions](#user-roles--permissions)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Third-Party Integrations](#third-party-integrations)
- [Background Tasks (Celery)](#background-tasks-celery)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Cloud Deployment (GCP)](#cloud-deployment-gcp)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Assignment Checklist](#assignment-checklist)

---

## Overview

TaskFlow is a task review platform where **Users** submit tasks for review, **Managers** approve or reject them, and **Admins** oversee the entire system. When a task status changes, the submitting user receives an automated email notification sent asynchronously via Celery and the Brevo transactional email API.

The application is containerized with Docker, deployed on Google Cloud Run, and ships with a CI/CD pipeline that automatically builds and deploys on every push to the `master` branch via Google Cloud Build.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 5.2 + Django REST Framework 3.15 |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Database | PostgreSQL (hosted on Supabase) |
| Task Queue | Celery 5.4 |
| Celery Broker | SQLAlchemy PostgreSQL (`sqla+postgresql://`) |
| Email Service | Brevo (Sendinblue) Transactional Email API |
| Frontend | React 19 + Vite 8 + Tailwind CSS 4 |
| HTTP Client | Axios |
| Containerization | Docker (multi-stage builds) |
| Cloud Platform | Google Cloud Platform — Cloud Run |
| CI/CD | Google Cloud Build |
| Image Registry | Google Artifact Registry |
| Secrets | Google Secret Manager |

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Google Cloud Run                        │
│                                                          │
│  ┌───────────────┐    REST API    ┌──────────────────┐   │
│  │  React + Vite │ ─────────────▶│  Django + DRF    │   │
│  │  (Frontend)   │◀─────────────  │  (Backend)       │   │
│  └───────────────┘    JSON        └────────┬─────────┘   │
│                                            │             │
│                              ┌─────────────┼──────────┐  │
│                              │             │          │  │
│                    ┌─────────▼──┐   ┌──────▼───────┐  │  │
│                    │ PostgreSQL  │   │ Celery Worker│  │  │
│                    │ (Supabase) │   │   (Cloud Run)│  │  │
│                    └────────────┘   └──────┬───────┘  │  │
│                                            │          │  │
│                                    ┌───────▼────────┐ │  │
│                                    │  Brevo Email   │ │  │
│                                    │      API       │ │  │
│                                    └────────────────┘ │  │
│                                                        │  │
└──────────────────────────────────────────────────────────┘
```

---

## User Roles & Permissions

| Action | User | Manager | Admin |
|---|:---:|:---:|:---:|
| Login / Refresh token | ✅ | ✅ | ✅ |
| Create a task | ✅ | — | — |
| View own tasks | ✅ | — | — |
| Update own email/password | ✅ | ✅ | ✅ |
| View tasks assigned to me | — | ✅ | — |
| Approve / Reject a task | — | ✅ | — |
| List all managers | ✅ | ✅ | ✅ |
| List all users (system-wide) | — | — | ✅ |
| List all tasks (system-wide) | — | — | ✅ |
| View system overview stats | — | — | ✅ |
| Invite new users | — | — | ✅ |

---

## Features

### User
- Register / log in with JWT authentication
- Create tasks and assign them to a manager
- Track task status: `PENDING` → `APPROVED` or `REJECTED`
- Receive email notification when task status changes
- Update profile email and password

### Manager
- View all tasks assigned to them
- Approve or reject pending tasks (triggers email to submitter)
- Update profile email and password

### Admin
- Invite new users (any role) via email with temporary credentials
- View a list of all users in the system
- View all tasks across all users
- Access a live dashboard overview:
  - Total users, total tasks
  - Breakdown by task status (Pending / Approved / Rejected)
  - Breakdown by user role (Admin / Manager / User)

---

## API Endpoints

### Authentication

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/auth/token/` | No | Login — returns `access` + `refresh` JWT |
| `POST` | `/api/auth/token/refresh/` | No | Exchange refresh token for new access token |

### Profile

| Method | Path | Role | Description |
|---|---|---|---|
| `PATCH` | `/api/profile/email/` | Any | Update own email (requires current password) |
| `POST` | `/api/profile/password/` | Any | Update own password |

### Tasks

| Method | Path | Role | Description |
|---|---|---|---|
| `POST` | `/api/tasks/` | User | Create a new task |
| `GET` | `/api/tasks/mine/` | User | List tasks created by the current user |
| `GET` | `/api/tasks/assigned/` | Manager | List tasks assigned to the current manager |
| `PATCH` | `/api/tasks/<id>/status/` | Manager | Update task status (`APPROVED` / `REJECTED`) |

### Admin

| Method | Path | Role | Description |
|---|---|---|---|
| `GET` | `/api/managers/` | Any (auth) | List all managers |
| `GET` | `/api/admin/users/` | Admin | List all users |
| `GET` | `/api/admin/tasks/` | Admin | List all tasks |
| `GET` | `/api/admin/overview/` | Admin | System statistics dashboard |
| `POST` | `/api/admin/invite/` | Admin | Invite a new user by email |

---

## Third-Party Integrations

### Brevo (Transactional Email API)

Brevo is used to send two types of automated emails:

| Trigger | Recipient | Content |
|---|---|---|
| Task status changes to `APPROVED` or `REJECTED` | Task creator | Notification with task title and new status |
| Admin invites a new user | Invited user | Welcome email with username and temporary password |

Emails are sent **asynchronously** via Celery — the API response is never blocked waiting for email delivery. All Brevo credentials are stored as environment variables (`BREVO_API_KEY`, `BREVO_SENDER_EMAIL`, `BREVO_SENDER_NAME`) and never hardcoded.

---

## Background Tasks (Celery)

Celery is configured with a **SQLAlchemy PostgreSQL broker** (same Supabase database, separate connection protocol) and Django database as the result backend.

| Task | Module | Trigger | Retries |
|---|---|---|---|
| `send_task_status_email` | `tasks.email_tasks` | Manager approves/rejects a task | 3x, 60s delay |
| `send_invitation_email` | `accounts.email_tasks` | Admin invites a new user | 3x, 60s delay |

In development (`DEBUG=True`), Celery tasks execute **eagerly** (synchronously) so no separate worker process is needed. In production, a dedicated Celery worker runs as its own Cloud Run service.

---

## Local Development Setup

### Prerequisites

Make sure the following are installed on your machine:

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 20+](https://nodejs.org/)
- [PostgreSQL](https://www.postgresql.org/download/) (or use a free [Supabase](https://supabase.com/) project)
- [Docker + Docker Compose](https://docs.docker.com/get-docker/) (optional, for containerized setup)
- Git

---

### Option A — Manual Setup (Recommended for Development)

#### 1. Clone the Repository

```bash
git clone https://github.com/NamanGupta123/bharat_intelligence_assignment.git
cd bharat_intelligence_assignment
```

#### 2. Backend Setup

```bash
cd Backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Configure Backend Environment

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
SECRET_KEY=your-50-char-django-secret-key
DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/taskflow
CELERY_BROKER_URL=sqla+postgresql://postgres:password@localhost:5432/taskflow
BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=your-verified-sender@example.com
BREVO_SENDER_NAME=Task Manager
FRONTEND_URL=http://localhost:5173
```

> **Note:** For `CELERY_BROKER_URL`, URL-encode any special characters in the password (e.g., `@` → `%40`, `#` → `%23`).

#### 4. Run Database Migrations

```bash
python manage.py migrate
```

#### 5. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

When prompted, set the role to `ADMIN` or update it via the Django admin panel at `/admin/`.

#### 6. Start the Backend Server

```bash
python manage.py runserver
# API available at http://127.0.0.1:8000
```

#### 7. (Optional) Start Celery Worker

In a second terminal (with the virtual environment activated):

```bash
cd Backend
celery -A config worker --loglevel=info
```

> With `DEBUG=True`, Celery tasks run synchronously — you only need this for production-like testing.

#### 8. Frontend Setup

In a new terminal:

```bash
cd Frontend

# Install dependencies
npm install
```

#### 9. Configure Frontend Environment

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

#### 10. Start the Frontend Dev Server

```bash
npm run dev
# App available at http://localhost:5173
```

---

### Option B — Docker Compose (Production-Like)

Runs all three services (backend, celery worker, frontend) as containers.

```bash
# From the project root
cp Backend/.env.example Backend/.env
# Edit Backend/.env with your values

cp Frontend/.env.example Frontend/.env.local
# Edit Frontend/.env.local with your values

docker compose -f docker-compose.prod.yml up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |

---

## Environment Variables

### Backend (`Backend/.env`)

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key (50+ chars) | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` / `False` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `CELERY_BROKER_URL` | Celery broker (SQLAlchemy format) | `sqla+postgresql://user:pass@host/db` |
| `BREVO_API_KEY` | Brevo API key for emails | `xkeysib-...` |
| `BREVO_SENDER_EMAIL` | Verified sender address in Brevo | `no-reply@yourdomain.com` |
| `BREVO_SENDER_NAME` | Display name for sent emails | `Task Manager` |
| `FRONTEND_URL` | Allowed CORS origin | `http://localhost:5173` |

### Frontend (`Frontend/.env.local`)

| Variable | Description | Example |
|---|---|---|
| `VITE_API_BASE_URL` | Base URL for all API calls | `http://127.0.0.1:8000` |

---

## Cloud Deployment (GCP)

The application runs on **Google Cloud Run** — a fully managed, serverless container platform. Three Cloud Run services are deployed:

| Service | Cloud Run Name | Description |
|---|---|---|
| Django API | `taskflow-backend` | Serves REST API on port 8000 |
| React App | `taskflow-frontend` | Serves static frontend on port 3000 |
| Celery Worker | `taskflow-celery` | Processes background email tasks |

All secrets are stored in **Google Secret Manager** and injected at runtime — no secrets are baked into Docker images or environment files.

### Manual Deployment Steps

1. Enable APIs: Cloud Run, Cloud Build, Artifact Registry, Secret Manager
2. Create an Artifact Registry repository: `app-repo` in `us-central1`
3. Store all secrets in Secret Manager with the names listed in `cloudbuild.yaml`
4. Connect your GitHub repository to Cloud Build
5. Push to `master` — Cloud Build handles the rest automatically

---

## CI/CD Pipeline

Every push to the `master` branch triggers a Google Cloud Build pipeline defined in [`cloudbuild.yaml`](cloudbuild.yaml):

```
Push to master
     │
     ▼
Cloud Build triggered
     │
     ├─ 1. Build backend Docker image
     ├─ 2. Push backend image → Artifact Registry
     ├─ 3. Build frontend Docker image (injects API URL at build time)
     ├─ 4. Push frontend image → Artifact Registry
     ├─ 5. Deploy taskflow-backend → Cloud Run
     ├─ 6. Deploy taskflow-frontend → Cloud Run
     └─ 7. Deploy taskflow-celery → Cloud Run (private, min 1 instance)
```

Build logs are captured in Google Cloud Logging (`CLOUD_LOGGING_ONLY`).

---

## Project Structure

```
bharat_intelligence_assignment/
├── Backend/
│   ├── accounts/
│   │   ├── models.py          # Custom User model (ADMIN, MANAGER, USER roles)
│   │   ├── serializers.py     # Auth, profile, invite serializers
│   │   ├── views.py           # Auth, profile, admin user views
│   │   ├── permissions.py     # Role-based permission classes
│   │   ├── urls.py            # accounts URL patterns
│   │   └── email_tasks.py     # Celery task: send invitation email
│   ├── tasks/
│   │   ├── models.py          # Task model (PENDING, APPROVED, REJECTED)
│   │   ├── serializers.py     # Task serializers
│   │   ├── views.py           # Task CRUD + admin views
│   │   ├── urls.py            # tasks URL patterns
│   │   └── email_tasks.py     # Celery task: send status change email
│   ├── config/
│   │   ├── settings.py        # Django + Celery configuration
│   │   ├── urls.py            # Root URL configuration
│   │   ├── celery.py          # Celery app initialization
│   │   └── wsgi.py
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── Frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── LoginPage.jsx      # JWT login form
│   │   │   ├── UserView.jsx       # User dashboard
│   │   │   ├── ManagerView.jsx    # Manager dashboard
│   │   │   └── AdminView.jsx      # Admin dashboard
│   │   ├── context/
│   │   │   └── AuthContext.jsx    # Global auth state
│   │   ├── api/
│   │   │   └── axios.js           # Axios instance with Bearer token
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.prod.yml    # Production multi-service compose
├── cloudbuild.yaml            # GCP Cloud Build CI/CD pipeline
└── Readme.md
```

---

## Assignment Checklist

| Requirement | Status | Details |
|---|:---:|---|
| **Multi-User System (3+ roles)** | ✅ | Admin, Manager, User — each with distinct permissions |
| **Backend with Django + PostgreSQL** | ✅ | Django 5.2, DRF 3.15, PostgreSQL via Supabase |
| **Background Task Processing (Celery)** | ✅ | Email notifications via Celery workers |
| **REST API** | ✅ | 12 endpoints across auth, tasks, and admin |
| **Third-Party API Integration** | ✅ | Brevo Transactional Email API |
| **Cloud Deployment (GCP)** | ✅ | Live on Google Cloud Run (`us-central1`) |
| **Version Control + CI/CD** | ✅ | GitHub + Google Cloud Build auto-deploys on push |
