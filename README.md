# Mini SMS Gateway

A REST API developed for the **Nest Nepal Business Solutions — Backend Developer Intern** take-home assignment. It validates Nepali mobile numbers, calculates SMS costs, deducts wallet credits, and sends messages through simulated SMS providers with automatic failover and refunds.

## Tech Stack

- Python, Django 6.1.2, Django REST Framework 3.18.3
- PostgreSQL for transactional wallet operations and row-level locking
- Simple JWT for authentication
- django-filter for SMS log filtering
- pytest and pytest-django for tests
- Docker and Docker Compose for containerized development

## Features

- User registration and JWT login; one credit wallet per user
- Nepali mobile number validation and normalization (`97`/`98`, optional `+977` or `977`)
- GSM-7 and Unicode SMS segment counting, including GSM-7 extension characters
- Credit calculation: **SMS parts × number of recipients**, at one credit per part
- Transaction-safe wallet debit and refund records
- Mock providers with priority, balance, configurable failure rate, and automatic failover
- Paginated, user-specific SMS logs with status, date, and phone-number filters
- Provider health reporting based on the last 24 hours of attempts

## Setup

Choose either Docker Compose or the local Python setup.

### Option A: Docker Compose (Recommended)

**Requirements:**
- Docker Engine
- Docker Compose v2 (included with Docker Desktop)

**1. Clone the repository**

```bash
git clone https://github.com/Sant7611/mini_sms_gateway.git
cd mini_sms_gateway
```

**2. Configure environment variables**

Create a `.env` file from the provided example.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

Update the `.env` file with your database password and a private Django secret key.

```dotenv
SECRET_KEY=replace-with-a-secure-secret-key
DEBUG=False

DB_ENGINE=django.db.backends.postgresql
DB_NAME=mini_sms_gateway
DB_USER=postgres
DB_PWD=replace-with-your-postgres-password
DB_HOST=localhost
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

Keep `.env` out of Git. It is already included in `.gitignore`.

**3. Build and start the containers**

Run from the repository root:

```bash
docker compose up --build -d
```

This starts:
- Django application on port `8000`
- PostgreSQL 16 database
- A persistent Docker volume for PostgreSQL data

**4. Check database readiness**

```bash
docker compose exec db pg_isready -U postgres -d mini_sms_gateway
```

Wait until PostgreSQL reports that it is accepting connections.

If you changed the database username or database name in `.env`, use those values in the command.

**5. Apply database migrations**

```bash
docker compose exec web python manage.py migrate
```

**6. Load mock SMS providers**

```bash
docker compose exec web python manage.py loaddata seed_providers.json
```

The fixture is stored at:

`backend/apps/providers/fixtures/seed_providers.json`

It initializes three simulated SMS providers with different priorities, balances, and failure rates.

Load this fixture into a fresh database. Loading it again can reset provider balances to their fixture values.

**7. Access the API**

```text
http://127.0.0.1:8000/
```

**Useful Docker commands**

View application logs:

```bash
docker compose logs -f web
```

View database logs:

```bash
docker compose logs -f db
```

Stop containers while preserving database data:

```bash
docker compose down
```

Stop containers and remove the database volume:

```bash
docker compose down -v
```

**Note:** The current Docker Compose configuration does not automatically run migrations or load provider fixtures. These are manual setup steps. The Django container currently uses the development server, so this configuration is intended for local development rather than production deployment.

### Option B: Local Python Setup

**Requirements:**
- Python 3.12
- PostgreSQL
- Git

**1. Clone the repository**

```bash
git clone https://github.com/Sant7611/mini_sms_gateway.git
cd mini_sms_gateway
```

Create the `.env` file in the repository root:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

**2. Configure PostgreSQL**

Create a local PostgreSQL database named `mini_sms_gateway`.

For example, using `psql`:

```sql
CREATE DATABASE mini_sms_gateway;
```

Update the root `.env` file with your local database credentials:

```dotenv
SECRET_KEY=replace-with-a-local-development-secret
DEBUG=True

DB_ENGINE=django.db.backends.postgresql
DB_NAME=mini_sms_gateway
DB_USER=postgres
DB_PWD=replace-with-your-postgres-password
DB_HOST=localhost
DB_PORT=5432

ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important:** Django loads `.env` from the repository root, not from the `backend/` directory.

**3. Create and activate a virtual environment**

```bash
cd backend
python -m venv venv
```

Windows PowerShell:

```powershell
./venv/Scripts/Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Apply database migrations**

```bash
python manage.py migrate
```

**6. Load mock providers**

```bash
python manage.py loaddata seed_providers.json
```

The fixture is located at `apps/providers/fixtures/seed_providers.json`.

Load it into a fresh database because loading it again may reset provider balances.

**7. Start the API**

```bash
python manage.py runserver
```

Base URL:

```text
http://127.0.0.1:8000/
```

**Configuration Notes**

- Do not commit `.env` or database credentials to Git.
- PostgreSQL is required to validate row-level locking and concurrent wallet deductions.
- The SQLite fallback is not suitable for validating the concurrency guarantee.
- The current Django settings assign `DEBUG = os.getenv("DEBUG", True)` without parsing the environment variable as a Boolean. Consequently, the string `DEBUG=False` is still truthy in Python. This should be corrected before public deployment.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register/` | Register an account and create its wallet |
| POST | `/api/v1/auth/login/` | Obtain JWT access and refresh tokens |
| POST | `/api/v1/sms/send/` | Validate recipients, charge credits, and attempt delivery |
| GET | `/api/v1/wallet/transactions/` | Extra route added just for viewing the transactions. |
| GET | `/api/v1/sms/logs/` | View your paginated SMS history |
| GET | `/routes/health/` | View provider balances and health |

Send and reporting endpoints require:

```text
Authorization: Bearer <access_token>
```

### Example SMS Request

```json
{
  "to": ["9841234567", "+9779801122334"],
  "message": "Hello from Nest SMS!"
}
```

### Example SMS Log Filters

Filter by status:

```text
/api/v1/sms/logs/?status=sent
```

Filter by date:

```text
/api/v1/sms/logs/?date=2026-10-29
```

Filter by phone number:

```text
/api/v1/sms/logs/?number=9841234567
```

Pagination:

```text
/api/v1/sms/logs/?page=1&page_size=20
```

## Design Decisions

- **One wallet per user:** A `OneToOneField` links each user to a single wallet balance.
- **One SMS record per recipient:** A batch request creates one message record per phone number, allowing independent sent/failed statuses and refunds.
- **SMS credits:** A GSM-7 message holds 160 units in one part or 153 per part when concatenated; Unicode uses 70 or 67. GSM-7 extension characters consume two units. Each part costs one credit per recipient.
- **PostgreSQL row locking:** `transaction.atomic()` and `select_for_update()` protect the balance check and deductions from concurrent overspending.
- **Wallet ledger:** `WalletTransaction` records debits and refunds. A uniqueness constraint prevents duplicate transactions of the same type for a message.
- **Priority-based failover:** The gateway tries providers with sufficient balance in priority order, recording each attempt. If every route fails for a recipient, that message's credits are refunded.
- **Synchronous mock delivery:** The current implementation performs database-backed mock provider operations in the same outer transaction as its wallet and message updates. Unexpected failures before commit roll back these database changes. Real external SMS delivery would require different transaction boundaries and recovery mechanisms.

## Route Health Formula

For each provider, attempts from the **last 24 hours** are counted.

Success rate:

```text
success_rate_24h = (successful_attempts / total_attempts) × 100
```

When no attempts exist, `success_rate_24h` is reported as `null`. The health calculation instead uses the configured success probability:

```text
effective_success_rate = (1 - failure_rate) × 100
```

Balance score:

```text
balance_score = min(provider_balance, 100)
```

Final health calculation:

```text
health = round(0.8 × effective_success_rate + 0.2 × balance_score)
```

**Exception:** If provider balance is zero, health is **0**.

Success rate receives 80% weight because delivery reliability matters more than remaining balance. Balance receives 20% because a depleted route cannot send more messages.

For example, an 80% measured success rate and a balance of 100 gives:

```text
health = 0.8 × 80 + 0.2 × 100
health = 84
```

## Tests

Run the test suite from `backend/` with PostgreSQL configured.

**Local Python setup:**

```bash
pytest -v
```

**Docker setup:**

```bash
docker compose exec web pytest -v
```

The test suite covers:

- Nepali mobile number normalization and invalid number rejection
- GSM-7 and Unicode SMS segmentation boundaries
- Provider priority-based failover
- Concurrent wallet deductions

The concurrency test simulates **20 simultaneous one-credit SMS requests competing for 10 wallet credits**.

Expected outcome:

- 10 successful requests
- 10 rejected requests
- Wallet balance of 0 credits

## Improvements

### Improvements to the Current Implementation

- Add more automated checks for all-provider failure, refunds, and transaction rollback.
- Make API error responses more consistent for failed send operations.
- Expose provider attempt details in logs to simplify troubleshooting.
- Improve phone-number normalization in SMS log filters.
- Correct Boolean parsing of the Django `DEBUG` environment variable.
- Add automated database migration and provider initialization to the deployment workflow.

### Future Enhancements

- Queue-based SMS processing with Celery and Redis.
- Per-user API rate limiting.
- Real SMS provider integrations and delivery-report webhooks.
- Idempotency and recovery for duplicate requests and interrupted external sends.

---

**Developed for the Nest Nepal Business Solutions — Backend Developer Intern Take-Home Assignment.**