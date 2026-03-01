# Private Auth Box — FastAPI Backend

Self-managed backend replacing Supabase Edge Functions and Supabase Auth.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for the frontend)

## Quick Start

### 1. Database setup

```bash
# Create a PostgreSQL database
createdb authbox
```

### 2. Backend setup

```bash
cd backend

# Create a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env
# Edit .env with your database URL and a strong SECRET_KEY

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API is now available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3. Frontend setup

```bash
# From the project root (not backend/)
npm install
npm run dev
```

The frontend runs at `http://localhost:8080` and expects the API at `http://localhost:8000/api` (configurable via `VITE_API_URL` in `.env`).

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string (asyncpg) | `postgresql+asyncpg://postgres:postgres@localhost:5432/authbox` |
| `SECRET_KEY` | JWT signing secret (change in production!) | `change-me-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `60` |
| `FRONTEND_URL` | Allowed CORS origin | `http://localhost:8080` |
| `MAIL_MODE` | `console` (prints reset links) or `smtp` | `console` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | SMTP settings (when `MAIL_MODE=smtp`) | — |

### Frontend (`.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000/api` |

## API Endpoints

### Auth

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/signup` | Register a new account | No |
| POST | `/api/auth/signin` | Login, returns JWT | No |
| POST | `/api/auth/signout` | Logout (client discards token) | No |
| GET | `/api/auth/me` | Get current user | Yes |
| POST | `/api/auth/reset-password` | Request password reset email | No |
| POST | `/api/auth/reset-password-confirm?token=...` | Confirm reset with token | No |
| POST | `/api/auth/update-password` | Update password (authenticated) | Yes |

### OTP Accounts

| Method | Path | Description | Auth |
|---|---|---|---|
| GET | `/api/otp-accounts/` | List all accounts | Yes |
| POST | `/api/otp-accounts/` | Create an account | Yes |
| PATCH | `/api/otp-accounts/{id}` | Update issuer/account_name | Yes |
| DELETE | `/api/otp-accounts/{id}` | Delete an account | Yes |

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |

## Architecture Notes

- **Authentication**: JWT-based (stateless). Tokens are stored in `localStorage` on the frontend.
- **Encryption**: OTP secrets are encrypted client-side using AES-256-GCM with PBKDF2 key derivation. The backend only stores ciphertext — it never sees the plaintext secrets.
- **Password reset**: In `console` mode, reset links are printed to the terminal. In `smtp` mode, connect your SMTP server.
- **Database**: Async PostgreSQL via SQLAlchemy 2.0 + asyncpg. Migrations via Alembic.
