#!/usr/bin/env python3
"""Day 2 starter checkpoint — brings the environment to a functionally
equivalent end-of-Lab-2 state.

Run this at the start of Day 2 (or whenever your tables got into a weird
state). It rebuilds everything the Day 2 labs depend on, regardless of
whether Labs 1-2 were completed on this machine:

  1. Restores the `source_orders` table in PostgreSQL `source_db`.
     (Note: recreated via JDBC overwrite, so the PRIMARY KEY / NOT NULL
     constraints from seed_source_data.sql are not reapplied — same data,
     looser DDL; nothing on Day 2 depends on the constraints.)
  2. Rebuilds `hive_prod.db.orders_lakehouse`, replaying the full Lab 2
     history — original schema, first batch, schema evolution, second
     batch — so the table has ≥ 2 snapshots for time travel.

Usage (from the repo root, stack running):

  docker exec spark-jupyter bash -c \
    'source /usr/local/bin/before-notebook.d/spark-config.sh && \
     python3 /home/jovyan/scripts/lab_03/day2_starter_checkpoint.py'
"""
from datetime import datetime
from decimal import Decimal

from pyspark.sql import SparkSession
from pyspark.sql.types import (BooleanType, DecimalType, IntegerType,
                               StructField, StructType, TimestampType)

TABLE = "hive_prod.db.orders_lakehouse"
JDBC_OPTS = {
    "url": "jdbc:postgresql://postgres:5432/source_db",
    "dbtable": "source_orders",
    "user": "admin",
    "password": "password",
    "driver": "org.postgresql.Driver",
}

# --- The Lab 2 data ---------------------------------------------------------
BATCH_1_SCHEMA = StructType([
    StructField("order_id",        IntegerType(),     False),
    StructField("customer_id",     IntegerType(),     False),
    StructField("order_amount",    DecimalType(10, 2), False),
    StructField("order_timestamp", TimestampType(),   False),
])
BATCH_1 = [
    (1,  101, Decimal("49.99"),  datetime(2026, 6, 28,  8, 15, 23)),
    (2,  102, Decimal("129.50"), datetime(2026, 6, 28, 11, 42, 10)),
    (3,  103, Decimal("15.00"),  datetime(2026, 6, 28, 19,  3, 45)),
    (4,  101, Decimal("220.75"), datetime(2026, 6, 29,  9, 27, 31)),
    (5,  104, Decimal("75.20"),  datetime(2026, 6, 29, 14, 55,  2)),
    (6,  105, Decimal("33.10"),  datetime(2026, 6, 29, 21, 18, 47)),
    (7,  102, Decimal("310.00"), datetime(2026, 6, 30,  7, 44, 12)),
    (8,  106, Decimal("58.60"),  datetime(2026, 6, 30, 12, 30, 59)),
    (9,  103, Decimal("92.35"),  datetime(2026, 6, 30, 16, 22,  8)),
    (10, 107, Decimal("480.99"), datetime(2026, 7, 1, 10,  5, 41)),
    (11, 104, Decimal("27.45"),  datetime(2026, 7, 1, 13, 37, 26)),
    (12, 108, Decimal("64.80"),  datetime(2026, 7, 1, 18, 59, 54)),
    (13, 105, Decimal("150.00"), datetime(2026, 7, 2,  8, 41, 19)),
    (14, 109, Decimal("88.88"),  datetime(2026, 7, 2, 15, 12, 33)),
    (15, 110, Decimal("19.99"),  datetime(2026, 7, 2, 22, 48,  7)),
]

BATCH_2_SCHEMA = StructType([
    StructField("order_id",         IntegerType(),     False),
    StructField("customer_id",      IntegerType(),     False),
    StructField("order_amount",     DecimalType(12, 2), False),
    StructField("order_timestamp",  TimestampType(),   False),
    StructField("discount_applied", BooleanType(),     True),
])
BATCH_2 = [
    (16, 111, Decimal("15499.00"), datetime(2026, 7, 3,  9, 14, 55), True),
    (17, 103, Decimal("42.75"),    datetime(2026, 7, 3, 12, 40, 18), False),
    (18, 112, Decimal("310.20"),   datetime(2026, 7, 3, 17,  5, 33), True),
    (19, 105, Decimal("88.00"),    datetime(2026, 7, 4,  8, 22, 41), False),
    (20, 113, Decimal("1249.99"),  datetime(2026, 7, 4, 14, 58,  2), True),
]


def main() -> None:
    spark = SparkSession.builder.appName("Day2-StarterCheckpoint").getOrCreate()
    df_batch1 = spark.createDataFrame(BATCH_1, schema=BATCH_1_SCHEMA)
    df_batch2 = spark.createDataFrame(BATCH_2, schema=BATCH_2_SCHEMA)

    print("[1/2] Restoring source_orders in PostgreSQL (source_db)...")
    writer = df_batch1.write.format("jdbc").mode("overwrite")
    for k, v in JDBC_OPTS.items():
        writer = writer.option(k, v)
    writer.save()
    print("      done — 15 rows.")

    print(f"[2/2] Rebuilding {TABLE} with full Lab 2 history...")
    spark.sql(f"DROP TABLE IF EXISTS {TABLE} PURGE")
    spark.sql(f"""
        CREATE TABLE {TABLE} (
            order_id        INT,
            customer_id     INT,
            order_amount    DECIMAL(10,2),
            order_timestamp TIMESTAMP
        )
        USING iceberg
        PARTITIONED BY (days(order_timestamp))
    """)
    df_batch1.writeTo(TABLE).append()                       # snapshot 1
    spark.sql(f"""
        ALTER TABLE {TABLE}
        ADD COLUMNS (discount_applied BOOLEAN COMMENT 'Was a discount applied at checkout?')
    """)
    spark.sql(f"ALTER TABLE {TABLE} ALTER COLUMN order_amount TYPE DECIMAL(12,2)")
    df_batch2.writeTo(TABLE).append()                       # snapshot 2

    # --- Verify -------------------------------------------------------------
    rows = spark.table(TABLE).count()
    snapshots = spark.sql(f"SELECT * FROM {TABLE}.snapshots").count()
    assert rows == 20, f"expected 20 rows, found {rows}"
    assert snapshots >= 2, f"expected >= 2 snapshots, found {snapshots}"

    print()
    print("=" * 60)
    print("  Checkpoint complete — environment at end-of-Lab-2 state")
    print(f"    {TABLE}: {rows} rows, {snapshots} snapshots")
    print("    postgres source_db.source_orders: 15 rows")
    print("=" * 60)


if __name__ == "__main__":
    main()
