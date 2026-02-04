# FastAPI PostgreSQL JWT Authentication API

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org)

Production-ready REST API with JWT authentication, PostgreSQL database, and enterprise-level security middlewares.

---

## Features

### Authentication & Authorization
- JWT-based stateless authentication
- Secure password hashing with bcrypt
- Token blacklisting for logout
- Bulk user registration

### Security
- **Rate Limiting**: 100 requests/minute per IP
- **Login Protection**: Lock after 5 failed attempts (15-minute cooldown)
- **Security Headers**: XSS, clickjacking, MIME-sniffing protection
- **Request Size Limiting**: 1MB maximum payload
- **Idempotency**: Prevent duplicate operations
- **Input Sanitization**: XSS and SQL injection prevention

### Observability
- Request logging with unique IDs
- Performance monitoring
- Structured error handling

---

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 13+
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic v2
- **Server**: Uvicorn

---

## Project Structure

```
├── app/
│   ├── routes/
│   │   ├── auth.py              # Authentication endpoints
│   │   └── items.py             # CRUD operations
│   ├── main.py                  # App initialization & middleware
│   ├── config.py                # Database configuration
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py               # Pydantic schemas
│   ├── auth.py                  # JWT utilities
│   ├── dependencies.py          # Dependency injection
│   ├── middleware.py            # Security middlewares
│   ├── exception.py             # Exception handlers
│   └── validators.py            # Input validators
├── init.sql                     # Database initialization script
├── .env.example                 # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 13+

### Setup

**1. Create virtual environment and install dependencies**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Database setup**

Run the initialization script:
```bash
psql -U postgres -f init.sql
# Edit the password in init.sql before running
```

Or manually:
```sql
CREATE DATABASE project_a;
CREATE USER dbadmin WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE project_a TO dbadmin;

\c project_a
GRANT ALL ON SCHEMA public TO dbadmin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dbadmin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dbadmin;
```

**3. Environment configuration**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Generate secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` file:
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_a
DB_USER=your_user
DB_PASSWORD=your_password

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**4. Run**
```bash
uvicorn app.main:app --reload
```

Access at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Get JWT token |
| POST | `/auth/logout` | Blacklist token |
| POST | `/auth/register/bulk` | Bulk registration |

### Items (Protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/items/` | Create item |
| GET | `/items/` | List items |
| GET | `/items/{id}` | Get item |
| PUT | `/items/{id}` | Update item |
| DELETE | `/items/{id}` | Delete item |

---

## Usage Examples

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Create item
```bash
curl -X POST http://localhost:8000/items/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Item","description":"Description"}'
```

### List items
```bash
curl http://localhost:8000/items/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Security Features

### Rate Limiting
Limits to 100 requests per minute per IP.

**Test:**
```bash
for i in {1..105}; do curl -s http://localhost:8000/; done
```

**Result:**
```
{"message":"Welcome to Project A API"}
{"message":"Welcome to Project A API"}
...
{"message":"Welcome to Project A API"}  # Request 100
{"error":"Too many requests. Try again later."}  # Request 101
{"error":"Too many requests. Try again later."}  # Request 102
```

### Login Protection
Locks account for 15 minutes after 5 failed login attempts.

**Test:**
```bash
for i in {1..6}; do 
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}';
done
```

**Result:**
```json
{"detail":"Incorrect email or password"}
{"detail":"Incorrect email or password"}
{"detail":"Incorrect email or password"}
{"detail":"Incorrect email or password"}
{"detail":"Incorrect email or password"}
{"error":"Too many failed attempts. Try again in 15 minutes."}
```

### Idempotency
Same `Idempotency-Key` returns cached response without creating duplicate.

**Test:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Test1234!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# First request - creates item
curl -X POST http://localhost:8000/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: test-key-456" \
  -H "Content-Type: application/json" \
  -d '{"title":"Idempotent Item"}'

# Same key - returns cached (same ID)
curl -X POST http://localhost:8000/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Idempotency-Key: test-key-456" \
  -H "Content-Type: application/json" \
  -d '{"title":"Idempotent Item"}'
```

**Result:**
```json
// First request
{"id":4,"title":"Idempotent Item","description":null,"owner_id":2,"created_at":"2026-02-04T15:39:01.714262"}

// Second request (same ID, no duplicate created)
{"id":4,"title":"Idempotent Item","description":null,"owner_id":2,"created_at":"2026-02-04T15:39:01.714262"}
```

**Log output:**
```
2026-02-04 18:39:01 - Request 73312d2e: POST /items/ - Status 201 Duration 0.020s
2026-02-04 18:39:01 - Idempotent request detected: test-key-456
2026-02-04 18:39:01 - Request 9275f7b2: POST /items/ - Status 201 Duration 0.000s  ← Cached
```

### Security Headers
All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Cache-Control: no-store`
- `X-Request-ID: unique-uuid`

---

## Testing

Interactive API documentation: http://localhost:8000/docs

Features:
- Try It Out functionality
- Built-in authentication
- Request/response examples
- Schema validation

---

## Performance

- **Async/Await**: Non-blocking I/O
- **Connection Pooling**: SQLAlchemy
- **Pydantic V2**: Fast validation
- **Uvicorn**: High-performance ASGI

---

## License

MIT
