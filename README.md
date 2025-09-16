# 📡 Smart API Monitoring Service

A **FastAPI + Celery powered monitoring system** for tracking APIs, websites, and services in real-time.  
It schedules health checks, records metrics, and sends styled alerts (Email/SMS) when a monitor fails or responds slowly.

---

## 🚀 Features

- **User Accounts**
  - Secure authentication with ownership of monitors.

- **Monitors**
  - Create, edit, delete monitors.
  - Flexible check frequency (`frequency_sec`).
  - Auto-rescheduling on server restarts.
  - Per-monitor task management with Celery.

- **Metrics**
  - Tracks uptime, status codes, response latency, and errors.
  - Automatic cleanup available (by monitor or metric ID).

- **Alerts**
  - Triggered on failure, latency breach, or unexpected status code.
  - Sent asynchronously via Celery.
  - Styled Email support.
  - Users can view and delete their alerts (by ID, monitor, or channel).

- **Admin-friendly**
  - Logs task execution details.
  - Robust retry logic with Celery.
  - Works with PostgreSQL (SQLAlchemy ORM).

---

## 🏗️ Architecture

```mermaid
flowchart TD
    subgraph FastAPI
        UI[REST Endpoints]
        Auth[Auth Router]
        Monitors[Monitors Router]
        Metrics[Metrics Router]
        Alerts[Alerts Router]
    end

    subgraph DB[PostgreSQL]
        T1[Users Table]
        T2[Monitors Table]
        T3[Metrics Table]
        T4[Alerts Table]
    end

    subgraph Celery
        Worker1[Monitor Check Task]
        Worker2[Send Alert Task]
    end

    UI --> Monitors --> DB
    UI --> Metrics --> DB
    UI --> Alerts --> DB

    Monitors --> Worker1
    Worker1 --> Metrics
    Worker1 --> Worker2
    Worker2 --> Alerts
```

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI
- **Task Queue:** Celery with Redis broker
- **Database:** PostgreSQL + SQLAlchemy ORM
- **Auth:** JWT-based authentication
- **Email:** Custom alert service with async delivery
- **Logging:** Structured logs for monitoring

---

```bash

SmartApiMonitor/
├── app/
│   ├── api/              # FastAPI routers
│   │   ├── routes_auth.py
│   │   ├── routes_monitor.py
│   │   ├── routes_metrics.py
│   │   └── routes_alert.py
│   │   └── routes_celery.py
│   ├── core/             # Core configs (celery, scheduler)
│   ├── db.py             # Database session & Base
│   ├── models/           # SQLAlchemy models (User, Monitor, Metric, Alert)
│   ├── schemas/          # Pydantic validation schemas (User, Monitor, Metric, Alert)
│   ├── services/         # Business logic (alerts, monitors)
│   ├── tasks/            # Celery tasks
│   ├── utils/            # Utilities (auth, security, query)
│   ├── config.py         # Configuration
│   └── main.py           # Entry point
│
├── alembic/              # Alembic migrations
├── alembic.ini           # Alembic script
├── requirements.txt
└── README.md

```

---

## ⚡ Setup & Installation

- 1️⃣ Clone the Repository
```bash
git clone https://github.com/Johnkenzzy/SmartApiMonitor.git
cd SmartApiMonitor
```

- 2️⃣ Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate   # (Linux/Mac)
.venv\Scripts\activate      # (Windows)
```

- 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

- 4️⃣ Setup Environment Variables
***Create a .env file:***
```txt
APP_NAME=Smart API Monitor
VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development
JWT_SECRET_KEY=SuperSecretKey
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_URL=postgresql+psycopg2://username:password@host:port/db_name
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
SMTP_USERNAME=user@gmail.com
SMTP_PASSWORD=user_password
```


- 5️⃣ Run Database Migrations
```bash
alembic upgrade head
```

- 6️⃣ Start Services
***Run FastAPI:***
```bash
uvicorn app.main:app --reload
```
***Run Celery workers:***
```bash
celery -A app.core.celery_app.celery_app worker -l info -Q monitoring,alerts
celery -A app.core.celery_app.celery_app worker --loglevel=info
```

## 🔥 Usage

**Create a Monitor**
```txt
POST /monitors/
{
  "name": "Local API",
  "url": "https://example.com/api",
  "frequency_sec": 60,
  "max_latency_ms": 2000
}
```

---

## 🤝 Contributing

- Fork this repo
- Create your feature branch (git checkout -b feature/awesome-feature)
- Commit changes (git commit -m "Add awesome feature")
- Push to branch (git push origin feature/awesome-feature)
- Open a Pull Request

---

## 📜 License

- MIT License © 2025 — Johnkennedy Umeh