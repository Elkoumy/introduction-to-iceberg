# Lab 4 — Lakehouse Maintenance & Compaction

The final lab: production operations. You will deliberately create the **small files problem**
(hundreds of tiny Parquet files), measure it, fix it with **compaction**, then reclaim storage with
**snapshot expiry** and **orphan file removal** — finishing with a physical audit in MinIO.

## Prerequisites

The Lab 1 stack must be running (any state is fine — this lab creates its own table,
`hive_prod.db.bloated_table`, from scratch):

```bash
cd ../lab_01_environment_setup/docker
docker compose up -d
docker compose ps        # minio, postgres, hive-metastore, spark-jupyter Up/healthy
```

> If `lab_04/` doesn't appear in Jupyter's file browser, your `spark-jupyter` container predates
> this lab's mount — recreate it once: `docker compose up -d spark-jupyter`

## Do the lab

Open Jupyter at <http://localhost:8888> and launch **`lab_04/Lab_04_Compaction_Cleanup.ipynb`**.
Keep the MinIO console (<http://localhost:9001>, `admin` / `password`) open in a second tab — this
lab repeatedly sends you there to see what's *physically* in the bucket.

You'll practice:

| Step | Concept |
|---|---|
| Simulate | One vectorized write producing ~600 tiny files (no loops) |
| Audit | `SELECT ... FROM hive_prod.db.bloated_table.files` — count & size distribution |
| Compact | `CALL hive_prod.system.rewrite_data_files(table => 'db.bloated_table')` |
| Reclaim | `CALL hive_prod.system.expire_snapshots(...retain_last => 1)` |
| Sweep | `CALL hive_prod.system.remove_orphan_files(...)` on manufactured debris |
| Verify | Physical file counts in MinIO before/after |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `lab_04/` missing in Jupyter | `docker compose up -d spark-jupyter` (see prerequisites) |
| Compaction result shows `rewritten_data_files_count: 0` | You re-ran the CALL on an already-compacted table — re-run the notebook from the top to regenerate the bloat |
| Kernel feels stuck on the big write | ~600-file commits take ~30–60 s on a laptop — watch progress in the Spark UI at <http://localhost:4040> |
| Want a clean slate | Just re-run the notebook from the top — it drops and recreates the table |
