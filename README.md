# 🚀 FastAPI PostgreSQL JWT Authentication API

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)](https://jwt.io/)

> **Production-ready REST API** with enterprise-grade security features including JWT authentication, rate limiting, idempotency, and comprehensive request validation.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Security Features](#-security-features)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Testing](#-testing)

---

## ✨ Features

### 🔐 Authentication & Authorization
- ✅ JWT-based stateless authentication
- ✅ Secure password hashing with bcrypt
- ✅ Token blacklisting for logout functionality
- ✅ Bulk user registration support

### 🛡️ Security Middlewares
- **Rate Limiting**: 100 requests/minute per IP
- **Login Protection**: 5 failed attempts → 15-minute lockout
- **Security Headers**: XSS, clickjacking, MIME-sniffing protection
- **Request Size Limiting**: 1MB maximum payload
- **Idempotency**: Prevent duplicate operations
- **Input Sanitization**: XSS and SQL injection prevention

### 📊 Observability
- Request logging with unique IDs
- Performance monitoring (request duration)
- Structured error handling

### 🏗️ Best Practices
- Clean architecture with separation of concerns
- Pydantic validation for type safety
- SQLAlchemy ORM for database operations
- Comprehensive exception handling
- CORS support for frontend integration

---

## 🏛️ Architecture

\`\`\`
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────────────┐
│     FastAPI Application             │
│  ┌──────────────────────────────┐   │
│  │   Middleware Stack           │   │
│  │  • CORS                      │   │
│  │  • Request Size Limit        │   │
│  │  • Security Headers          │   │
│  │  • Rate Limiting             │   │
│  │  • Login Attempt Tracking    │   │
│  │  • Idempotency               │   │
│  │  • Request Logging           │   │
│  └──────────────────────────────┘   │
│                                     │
│  ┌──────────────────────────────┐   │
│  │   Routes & Controllers       │   │
│  │  • /auth (register, login)   │   │
│  │  • /items (CRUD)             │   │
│  └──────────────────────────────┘   │
│                                     │
│  ┌──────────────────────────────┐   │
│  │   Business Logic             │   │
│  │  • Auth (JWT, bcrypt)        │   │
│  │  • Validators                │   │
│  │  • Dependencies              │   │
│  └──────────────────────────────┘   │
│                                     │
│  ┌──────────────────────────────┐   │
│  │   Data Layer                 │   │
│  │  • SQLAlchemy ORM            │   │
│  │  • Models & Schemas          │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │  PostgreSQL  │
        └──────────────┘
\`\`\`

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI |
| **Database** | PostgreSQL 13+ |
| **ORM** | SQLAlchemy |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt |
| **Validation** | Pydantic v2 |
| **ASGI Server** | Uvicorn |
| **Python Version** | 3.12+ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- pip or conda

### Installation

**1. Clone the repository**
\`\`\`bash
git clone https://github.com/mkyen/fastapi-postgresql-jwt-authentication-api.git
cd fastapi-postgresql-jwt-authentication-api
\`\`\`

**2. Create and activate virtual environment**
\`\`\`bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
\`\`\`

**3. Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**4. Setup PostgreSQL database**
\`\`\`sql
CREATE DATABASE project_a;
CREATE USER dbadmin WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE project_a TO dbadmin;

-- Connect to database
\c project_a

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO dbadmin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dbadmin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dbadmin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO dbadmin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO dbadmin;
\`\`\`

**5. Configure environment variables**
\`\`\`bash
cp .env.example .env
# Edit .env with your actual credentials
\`\`\`

**6. Run the application**
\`\`\`bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

🎉 **API is now running at:**
- API: http://localhost:8000
- Interactive Docs (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
\`\`\`http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
\`\`\`

**Response (201 Created):**
\`\`\`json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-04T12:00:00"
}
\`\`\`

#### Login
\`\`\`http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
\`\`\`

#### Logout
\`\`\`http
POST /auth/logout
Authorization: Bearer {token}
\`\`\`

**Response (200 OK):**
\`\`\`json
{
  "message": "Logged out successfully"
}
\`\`\`

#### Bulk Register
\`\`\`http
POST /auth/register/bulk
Content-Type: application/json

{
  "users": [
    {"email": "user1@example.com", "password": "Pass123!"},
    {"email": "user2@example.com", "password": "Pass456!"}
  ]
}
\`\`\`

### Items Endpoints (🔒 Protected)

All items endpoints require JWT authentication via \`Authorization: Bearer {token}\` header.

#### Create Item
\`\`\`http
POST /items/
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "My Item",
  "description": "Item description"
}
\`\`\`

**Response (201 Created):**
\`\`\`json
{
  "id": 1,
  "title": "My Item",
  "description": "Item description",
  "owner_id": 1,
  "created_at": "2026-02-04T12:00:00"
}
\`\`\`

#### List Items
\`\`\`http
GET /items/
Authorization: Bearer {token}
\`\`\`

**Response (200 OK):**
\`\`\`json
[
  {
    "id": 1,
    "title": "My Item",
    "description": "Item description",
    "owner_id": 1,
    "created_at": "2026-02-04T12:00:00"
  }
]
\`\`\`

#### Get Item by ID
\`\`\`http
GET /items/{item_id}
Authorization: Bearer {token}
\`\`\`

#### Update Item
\`\`\`http
PUT /items/{item_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Updated Title",
  "description": "Updated description"
}
\`\`\`

#### Delete Item
\`\`\`http
DELETE /items/{item_id}
Authorization: Bearer {token}
\`\`\`

**Response (204 No Content)**

---

## 🛡️ Security Features

### 1. Rate Limiting
Prevents brute force attacks by limiting requests per IP.

\`\`\`bash
# Test rate limiting (Mac/Linux)
for i in {1..105}; do curl -s http://localhost:8000/; done
# After 100 requests, returns 429 Too Many Requests
\`\`\`

**Configuration:** \`max_requests=100, window=60\` (100 requests per minute)

### 2. Login Attempt Limiting
Protects against credential stuffing attacks.

\`\`\`bash
# Test login protection
for i in {1..6}; do 
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}';
done
# After 5 failed attempts, account locks for 15 minutes
\`\`\`

### 3. Idempotency
Prevents duplicate operations for POST/PUT/PATCH requests.

\`\`\`bash
# Same Idempotency-Key returns cached response
curl -X POST http://localhost:8000/items/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-key-123" \
  -d '{"title":"Test Item"}'

# Retry with same key - gets same response without creating duplicate
\`\`\`

### 4. Security Headers
All responses include these security headers:

\`\`\`http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Cache-Control: no-store
X-Request-ID: {unique-uuid}
\`\`\`

### 5. Input Sanitization
- HTML/Script tag removal
- SQL injection prevention
- XSS protection

### 6. Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

---

## 📁 Project Structure

\`\`\`
fastapi-postgresql-jwt-authentication-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization & middleware
│   ├── config.py               # Database connection & env config
│   ├── models.py               # SQLAlchemy database models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── auth.py                 # JWT & password hashing utilities
│   ├── dependencies.py         # Dependency injection (DB, auth)
│   ├── middleware.py           # Security middlewares
│   ├── exception.py            # Custom exception handlers
│   ├── validators.py           # Input validation & sanitization
│   │
│   └── routes/
│       ├── __init__.py
│       ├── auth.py             # Authentication endpoints
│       └── items.py            # CRUD endpoints for items
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── README.md                   # This file
\`\`\`

---

## ⚙️ Configuration

### Environment Variables

Create \`.env\` file from template:

\`\`\`bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_a
DB_USER=your_db_user
DB_PASSWORD=your_secure_password

# JWT Configuration
SECRET_KEY=your_secret_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
\`\`\`

### Generate Secure Secret Key

\`\`\`bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
\`\`\`

---

## 🧪 Testing

### Manual Testing with cURL

**Complete Test Flow:**

\`\`\`bash
# 1. Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}'

# 2. Login and save token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 3. Create an item
curl -X POST http://localhost:8000/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Item","description":"My first item"}'

# 4. List items
curl http://localhost:8000/items/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Update item (assuming ID is 1)
curl -X PUT http://localhost:8000/items/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Updated Title"}'

# 6. Delete item
curl -X DELETE http://localhost:8000/items/1 \
  -H "Authorization: Bearer $TOKEN"

# 7. Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer $TOKEN"
\`\`\`

### Interactive Testing

Visit **http://localhost:8000/docs** for Swagger UI with:
- 🎯 Try It Out functionality
- 🔐 Built-in authentication
- 📝 Request/response examples
- 📊 Schema validation

---

## 📈 Performance

- ⚡ **Async/Await** for non-blocking operations
- 🔄 **Connection Pooling** with SQLAlchemy
- 📦 **Pydantic V2** for fast validation
- 🚀 **Uvicorn** ASGI server

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (\`git checkout -b feature/AmazingFeature\`)
3. Commit your changes (\`git commit -m 'Add some AmazingFeature'\`)
4. Push to the branch (\`git push origin feature/AmazingFeature\`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 👤 Author

**Kemal Yenigun**
- GitHub: [@mkyen](https://github.com/mkyen)
- LinkedIn: [Kemal Yenigun](https://linkedin.com/in/kemalyenigun)

---

## 🙏 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Team](https://www.sqlalchemy.org/)
- [PostgreSQL Community](https://www.postgresql.org/)
- [Python Community](https://www.python.org/)

---

<div align="center">

**⭐ Star this repo if you find it useful! ⭐**

Made with ❤️ using FastAPI

</div>
