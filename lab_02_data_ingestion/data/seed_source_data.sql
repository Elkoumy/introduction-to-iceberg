-- Lab 2 seed data: simulates a production OLTP orders table in PostgreSQL.
-- Applied to the `source_db` database of the Lab 1 stack (see lab README).
-- Idempotent: safe to re-run — it rebuilds the table from scratch.

DROP TABLE IF EXISTS source_orders;

CREATE TABLE source_orders (
    order_id        INT PRIMARY KEY,
    customer_id     INT           NOT NULL,
    order_amount    DECIMAL(10,2) NOT NULL,
    order_timestamp TIMESTAMP     NOT NULL
);

-- 15 orders spread across 5 calendar days, so the day-partitioned Iceberg
-- table in the notebook ends up with multiple visible partitions.
INSERT INTO source_orders (order_id, customer_id, order_amount, order_timestamp) VALUES
    (1,  101,  49.99, '2026-06-28 08:15:23'),
    (2,  102, 129.50, '2026-06-28 11:42:10'),
    (3,  103,  15.00, '2026-06-28 19:03:45'),
    (4,  101, 220.75, '2026-06-29 09:27:31'),
    (5,  104,  75.20, '2026-06-29 14:55:02'),
    (6,  105,  33.10, '2026-06-29 21:18:47'),
    (7,  102, 310.00, '2026-06-30 07:44:12'),
    (8,  106,  58.60, '2026-06-30 12:30:59'),
    (9,  103,  92.35, '2026-06-30 16:22:08'),
    (10, 107, 480.99, '2026-07-01 10:05:41'),
    (11, 104,  27.45, '2026-07-01 13:37:26'),
    (12, 108,  64.80, '2026-07-01 18:59:54'),
    (13, 105, 150.00, '2026-07-02 08:41:19'),
    (14, 109,  88.88, '2026-07-02 15:12:33'),
    (15, 110,  19.99, '2026-07-02 22:48:07');
