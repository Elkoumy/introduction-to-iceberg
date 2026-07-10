# Lab 3 — Trino Querying & Time Travel

Day 2 begins! In this lab a **second query engine (Trino)** reads the exact same Iceberg tables
Spark wrote — no copies, no sync — and you use Iceberg's snapshot history to **time travel** and
**roll back** a bad write.

## 1. Confirm Trino is up

Trino boots with the rest of the stack (no profile flag needed), so if your Day 1 environment is
still running you're already good. From the repo root:

```bash
cd lab_01_environment_setup/docker
docker compose ps
```

You should see `trino` as `Up (healthy)`. If it's missing (e.g. you stopped the stack overnight),
bring everything back with:

```bash
docker compose up -d
```

Trino takes ~30–60 s to pass its healthcheck on first boot.

| UI | URL | Login |
|---|---|---|
| **Trino Web UI** | <http://localhost:8080/ui/> | any username (e.g. `student`), no password |

## 2. Reset to the Day 2 checkpoint

This rebuilds `source_orders` (PostgreSQL) and `hive_prod.db.orders_lakehouse` (Iceberg) to their
exact end-of-Lab-2 state — 20 rows, 2 snapshots — no matter what state Day 1 left them in:

```bash
# (the `source` line loads the container's Spark env — SPARK_HOME/PYTHONPATH —
#  which is normally set up only for the Jupyter server, not for docker exec)
docker exec spark-jupyter bash -c \
  'source /usr/local/bin/before-notebook.d/spark-config.sh && \
   python3 /home/jovyan/scripts/lab_03/day2_starter_checkpoint.py'
```

On Windows PowerShell, `\` is not a line-continuation character (PowerShell uses a backtick), so
run it as a single line — the single quotes keep `&&` from being parsed by PowerShell:

```powershell
docker exec spark-jupyter bash -c 'source /usr/local/bin/before-notebook.d/spark-config.sh && python3 /home/jovyan/scripts/lab_03/day2_starter_checkpoint.py'
```

Expected output ends with `Checkpoint complete — environment at end-of-Lab-2 state`.

## 3. Do the lab

Open Jupyter at <http://localhost:8888> and launch **`lab_03/Lab_03_Trino_Time_Travel.ipynb`**.

You'll practice:

| Step | Concept |
|---|---|
| Trino connection | `trino.dbapi.connect(host="trino", port=8080, catalog="iceberg", schema="db")` |
| Multi-engine reads | Trino reads Spark-written tables via the shared Hive Metastore + MinIO |
| Dialect switching | `hive_prod.db.t.snapshots` (Spark) vs `"t$snapshots"` (Trino), etc. |
| Time travel | Spark: `VERSION AS OF` / `FOR SYSTEM_TIME AS OF` — Trino: `FOR VERSION/TIMESTAMP AS OF` |
| Rollback | `CALL hive_prod.system.rollback_to_snapshot(...)` |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `trino` container missing | `docker compose up -d` from `lab_01_environment_setup/docker` — Trino boots with the rest of the stack |
| Trino `Up (health: starting)` for a while | Normal on first boot (~30–60 s); wait for `healthy` |
| Port 8080 already in use | Stop whatever holds it (`lsof -i :8080`; PowerShell: `Get-NetTCPConnection -LocalPort 8080 -State Listen`) or change Trino's host port in `docker-compose.yml` |
| `The token '&&' is not a valid statement separator` | You're in PowerShell and the `\` line breaks were pasted — use the single-line `docker exec` form in step 2 |
| `ModuleNotFoundError: No module named 'trino'` in Jupyter | Your Jupyter image predates this course version — `docker compose build spark-jupyter && docker compose up -d`, then restart the kernel |
| Notebook says fewer than 2 snapshots | Re-run the checkpoint script (step 2) |
| Trino query fails with `Schema 'db' does not exist` | Run the checkpoint script — it creates the schema/table |
