# Lab 1 — Environment Boot & First Tables

Welcome! In this lab you will boot the complete lakehouse stack used throughout the bootcamp and
create your first Apache Iceberg table.

## What you're booting

| Service | Image | Ports | Purpose |
|---|---|---|---|
| **MinIO** | `minio/minio` | 9000 (S3 API), 9001 (console) | S3-compatible object storage; holds the `warehouse` bucket |
| **PostgreSQL** | `postgres:16.3` | 5432 | Backing DB for the metastore (`metastore`) + OLTP source for Lab 2 (`source_db`) |
| **Hive Metastore** | `apache/hive:3.1.3` (custom) | 9083 | The Iceberg **catalog** |
| **Spark + Jupyter** | `jupyter/pyspark-notebook:spark-3.5.0` (custom) | 8888 (Jupyter), 4040 (Spark UI) | Compute + your notebooks |

All credentials in this lab are `admin` / `password`.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose v2) running, with **≥ 6 GB RAM** allocated
- Ports **9000, 9001, 5432, 9083, 8888, 4040** free on your machine
- ~6 GB of free disk (images + JARs)

## 1. Start the stack

```bash
cd lab_01_environment_setup/docker
docker compose up -d --build
```

The **first** run builds two images and pulls the rest — expect **5–15 minutes** depending on your
connection. Subsequent starts take seconds.

> **Apple Silicon note:** the Hive Metastore image is x86-only and runs via Rosetta emulation —
> this is expected and works fine (make sure "Use Rosetta for x86/amd64 emulation" is enabled in
> Docker Desktop settings, which is the default).

## 2. Verify the containers are healthy

```bash
docker compose ps
```

Expected state when ready (order may differ):

```
NAME             ...   STATUS
hive-metastore   ...   Up (healthy)
minio            ...   Up (healthy)
minio-init       ...   Exited (0)
postgres         ...   Up (healthy)
spark-jupyter    ...   Up
```

`minio-init` is a one-shot job — it creates the `warehouse` bucket and exits; `Exited (0)` is
normal. (A sixth service, **Trino**, joins the stack in Lab 3 via a compose profile — don't worry
about it today.) To watch the boot logs live:

```bash
docker compose logs -f hive-metastore
```

## 3. Open the UIs

| UI | URL | Login |
|---|---|---|
| **Jupyter** | <http://localhost:8888> | none (token disabled for the lab) |
| **MinIO console** | <http://localhost:9001> | `admin` / `password` |
| **Spark UI** | <http://localhost:4040> | appears once a Spark session is running |

In MinIO you should already see the (empty) **`warehouse`** bucket under *Object Browser*.

## 4. Do the lab

In Jupyter, open **`lab_01/Lab_01_First_Tables.ipynb`** and work through it top to bottom. You will create
a database and an Iceberg table, insert and query rows, and then inspect the files Iceberg wrote to
MinIO.

## Troubleshooting

| Symptom | Fix |
|---|---|
| A port is already in use | Stop whatever holds it (`lsof -i :8888`) or change the host-side port in `docker-compose.yml` |
| `hive-metastore` keeps restarting | `docker compose logs hive-metastore`; most often PostgreSQL wasn't healthy yet — `docker compose up -d` again |
| Notebook can't reach the metastore | Confirm `docker compose ps` shows `hive-metastore (healthy)`, then restart the notebook kernel |
| Want a 100 % clean slate | `docker compose down -v` (**deletes all table data and the metastore**), then `up -d` again |

## Stopping

```bash
docker compose --profile lab3 down        # stop, keep data (tables survive)
docker compose --profile lab3 down -v     # stop AND wipe MinIO + PostgreSQL volumes
```

(The `--profile lab3` flag also stops Trino if you've started it in Lab 3; it's harmless before
that.)
