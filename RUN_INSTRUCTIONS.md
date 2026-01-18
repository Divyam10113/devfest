# 🚀 Compliance Intelligence System - Setup & Run

This guide details how to run the fully integrated **Compliance Intelligence System** (Gateway + Compliance + Ingestion), powered by **Google Gemini**.

## 🐳 Quick Start (Docker) - Recommended

The easiest way to run the entire system is using Docker Compose. This orchestrates the database and all 3 microservices automatically.

### 1. Prerequisites
- Docker & Docker Compose installed.
- **Environment Files**: Create `.env` files in each service directory with your API keys.

**`pdf_chunking/.env`**
```env
LLAMA_CLOUD_API_KEY=your_llama_key
GOOGLE_API_KEY=your_gemini_key
```

**`compliance_service/.env`**
```env
GOOGLE_API_KEY=your_gemini_key
```

**`gateway_api/.env`**
```env
DATABASE_URL=postgresql://user:password@db/gateway_db
SECRET_KEY=your_secret_key
# Other defaults are fine for Docker
```

### 2. Run the System
From the root directory (`devfest/`), run:

```bash
docker-compose up --build
```

Access the APIs:
- **Gateway API**: `http://localhost:8000`
- **Ingestion Service**: `http://localhost:8002`
- **Compliance Service**: `http://localhost:8003`

### 3. Test
Run the test script (from your host machine, assuming you have python installed):
```bash
python3 test_gateway_flow.py
```

---

## 🛠 Manual Setup (Local Development)

If you prefer to run services individually without Docker (e.g., for debugging).

### 1. Database Setup
You need a PostgreSQL database running locally.
- Update `gateway_api/.env`: `DATABASE_URL=postgresql://user:pass@localhost:5432/your_db`
- Run Migrations: `cd gateway_api && python3 -m alembic upgrade head`

### 2. Start Services (3 Terminals)

**Terminal 1 (Ingestion Service):**
```bash
cd pdf_chunking
uvicorn app.main:app --port 8002 --loop asyncio
```

**Terminal 2 (Compliance Service):**
```bash
cd compliance_service
uvicorn app.main:app --port 8003
```

**Terminal 3 (Gateway API):**
```bash
cd gateway_api
uvicorn api.main:app --port 8000
```

---

## 🏗 Architecture

| Service | Port | Container Name | Description |
| :--- | :--- | :--- | :--- |
| **Gateway API** | `8000` | `gateway-api` | Auth, Chat History, API Entrypoint |
| **Ingestion Service** | `8002` | `ingestion-service` | PDF Parsing, Embeddings, Vector DB |
| **Compliance Service** | `8003` | `compliance-service` | RAG Logic, Gemini LLM |
| **Database** | `5432` | `gateway-db` | PostgreSQL (Users, History) |
