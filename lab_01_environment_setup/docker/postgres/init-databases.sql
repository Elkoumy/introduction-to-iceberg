-- Runs once on first startup (empty data volume).
-- `metastore` is created by POSTGRES_DB; this adds the OLTP source used in Lab 2.
CREATE DATABASE source_db;
GRANT ALL PRIVILEGES ON DATABASE source_db TO admin;
