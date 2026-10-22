# GPS Attendance System

> [!NOTE]
> WORKING IN PROGRESS
>

1. Install and run Docker Desktop.
2. Copy and rename `.env.example` to `.env`.
3. Run PostgreSQL and APIs:

```bash
docker compose up -d --wait postgres
python -m pip install -r requirements.txt
uvicorn main:app --reload
```
