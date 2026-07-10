# Lab 2 — The Ingestion Pipeline & Schema Evolution

You will extract an orders table from PostgreSQL (our stand-in for a production OLTP system),
load it into an Iceberg table with **hidden partitioning**, then evolve the table's schema live —
no downtime, no rewrites — and ingest a batch with the new schema.

## Prerequisites

Lab 2 reuses the **Lab 1 stack**. Make sure it is running:

```bash
cd ../lab_01_environment_setup/docker
docker compose up -d
docker compose ps        # all services Up/healthy (minio-init: Exited (0) is normal)
```

## 1. Seed the source database

Load the mock production data into PostgreSQL's `source_db` (from the `lab_02_data_ingestion/`
directory):

```bash
docker exec -i postgres psql -U admin -d source_db < data/seed_source_data.sql
```

On Windows PowerShell, `<` is not an input-redirection operator — pipe the file in instead:

```powershell
Get-Content data/seed_source_data.sql | docker exec -i postgres psql -U admin -d source_db
```

Expected output ends with `INSERT 0 15`. Verify:

```bash
docker exec postgres psql -U admin -d source_db -c "SELECT COUNT(*) FROM source_orders;"
```

You should see `15`. The script is idempotent — re-running it resets the table.

## 2. Do the lab

Open Jupyter at <http://localhost:8888> and launch **`lab_02/Lab_02_Ingestion_Evolution.ipynb`**.
This folder is mounted straight from the repo (`lab_02_data_ingestion/notebooks/`), so your work
is saved on your machine.

> If you started the stack before Lab 2 existed, recreate the Jupyter container once so the new
> mount appears: `cd ../lab_01_environment_setup/docker && docker compose up -d spark-jupyter`

## What you'll practice

| Step | Concept |
|---|---|
| JDBC extract | `spark.read.format("jdbc")` against `postgres:5432/source_db` |
| Hidden partitioning | `PARTITIONED BY (days(order_timestamp))` — no partition column in the schema |
| Load | `df.writeTo("hive_prod.db.orders_lakehouse").append()` |
| Schema evolution | `ALTER TABLE ... ADD COLUMNS`, safe type widening `DECIMAL(10,2) → DECIMAL(12,2)` |
| Verification | One `SELECT *` reading pre- and post-evolution rows side by side |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `relation "source_orders" does not exist` | You skipped step 1 — run the seed command |
| `The '<' operator is reserved for future use` | You're in PowerShell — use the `Get-Content ... \|` form of the seed command |
| `Connection refused` on JDBC read | `docker compose ps` in the Lab 1 folder; Postgres must be `Up (healthy)` |
| Notebook not visible in Jupyter | Recreate the container so the mount appears: `cd ../lab_01_environment_setup/docker && docker compose up -d spark-jupyter` |
| Want to restart the lab from scratch | Re-run the seed script; the notebook's first table cell drops and recreates the Iceberg table |
