# Fixora — Manual MySQL setup (`schema.sql`)

Use this when you want the **real MySQL database** from your thesis (`database/schema.sql`) instead of SQLite.

---

## What `schema.sql` creates

| Item | Contents |
|------|----------|
| Database | `fixora` (utf8mb4) |
| RBAC | `roles`, `users` |
| Enterprise | `orders`, `inventory` |
| Monitoring | `log_sources`, `log_entries`, `alerts` |
| Agents | `agent_runs`, `diagnostics`, `nl_queries` |
| Dashboard | `health_metrics` |
| Sample data | roles, log sources, 3 orders, 3 inventory rows |

**Demo login users are NOT in `schema.sql`.** After loading the schema, run:

```powershell
py -3 scripts\seed_admin.py
```

That creates `admin@fixora.local` / `admin123` and `viewer@fixora.local` / `viewer123`.

---

## Option A — MySQL installed on Windows (no Docker)

### Step 1 — Install MySQL 8

1. Download [MySQL Installer](https://dev.mysql.com/downloads/installer/) (Windows).
2. Install **MySQL Server 8.0** (or 8.4).
3. Set a **root password** during install (remember it).
4. Ensure **MySQL** is running (Services → *MySQL80* → Running).

### Step 2 — Add `mysql` to PATH (if needed)

Default location:

```
C:\Program Files\MySQL\MySQL Server 8.0\bin
```

Open PowerShell and check:

```powershell
mysql --version
```

### Step 3 — Create the Fixora database user

Open PowerShell in the project folder:

```powershell
cd "C:\Users\ishini.rathnayake\Desktop\my\University Projects\Fixora"
```

Run as **root** (enter your root password when prompted):

```powershell
mysql -u root -p < database\create_mysql_user.sql
```

This creates user `fixora` / password `fixora_dev_password` (matches `.env.example`).

### Step 4 — Run `schema.sql`

Still as root (simplest for first setup):

```powershell
mysql -u root -p < database\schema.sql
```

Or as the `fixora` user:

```powershell
mysql -u fixora -pfixora_dev_password < database\schema.sql
```

### Step 5 — Configure `.env` for MySQL

Edit `.env` in the project root:

```env
USE_SQLITE=false
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=fixora
MYSQL_PASSWORD=fixora_dev_password
MYSQL_DATABASE=fixora
```

### Step 6 — Seed demo users

```powershell
$env:USE_SQLITE="false"
py -3 scripts\seed_admin.py
```

Expected output:

```
Database initialized. Users: admin@fixora.local / admin123, viewer@fixora.local / viewer123
```

### Step 7 — Start backend and frontend

**Terminal 1 — API:**

```powershell
cd backend
$env:USE_SQLITE="false"
py -3 -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — UI:**

```powershell
cd frontend
npm run dev
```

Open **http://localhost:5173** and sign in.

---

## Option B — Automated script (after MySQL is running)

If `mysql` is on PATH and user `fixora` can connect:

```powershell
cd "C:\Users\ishini.rathnayake\Desktop\my\University Projects\Fixora"
.\scripts\setup-mysql.ps1
```

This runs `schema.sql`, sets `USE_SQLITE=false`, and seeds users.

---

## Option C — Docker for MySQL only (no full Docker app stack)

If you install **Docker Desktop** later but still run API/UI locally:

```powershell
cd "C:\Users\ishini.rathnayake\Desktop\my\University Projects\Fixora"
docker compose up -d mysql
```

Wait ~30 seconds. Docker auto-runs `schema.sql` on first start.

Then:

```powershell
$env:USE_SQLITE="false"
py -3 scripts\seed_admin.py
```

Start API and UI as in Step 7 above.

---

## Option D — Keep using SQLite (current local mode)

If you do **not** need MySQL for the demo:

```powershell
.\run-local.ps1
```

Uses `backend/data/fixora.db` — no `schema.sql` required. Tables are created by the Python app.

---

## Verify schema loaded

```powershell
mysql -u fixora -pfixora_dev_password -e "USE fixora; SHOW TABLES;"
```

You should see 12 tables including `roles`, `users`, `log_entries`, `alerts`, etc.

Check sample orders:

```powershell
mysql -u fixora -pfixora_dev_password -e "USE fixora; SELECT * FROM orders;"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `mysql: command not found` | Add MySQL `bin` folder to PATH or use full path to `mysql.exe` |
| `Access denied for user 'fixora'` | Run `create_mysql_user.sql` as root |
| `Can't connect to MySQL server` | Start MySQL service; check port 3306 |
| Login works on SQLite but not MySQL | Ensure `USE_SQLITE=false` and re-run `seed_admin.py` |
| `Table already exists` | DB already initialized — safe to skip schema or drop DB first |

### Reset database (start fresh)

```powershell
mysql -u root -p -e "DROP DATABASE IF EXISTS fixora;"
mysql -u root -p < database\schema.sql
$env:USE_SQLITE="false"
py -3 scripts\seed_admin.py
```

---

## SQLite vs MySQL

| | SQLite (`run-local.ps1`) | MySQL (`schema.sql`) |
|--|--------------------------|----------------------|
| Install | None extra | MySQL 8 or Docker |
| Thesis alignment | Good for prototype | Matches `schema.sql` / report ER diagram |
| File | `backend/data/fixora.db` | MySQL server `fixora` database |

For your dissertation report, you can document **both**: SQLite for easy local demo, MySQL for production-style schema.
