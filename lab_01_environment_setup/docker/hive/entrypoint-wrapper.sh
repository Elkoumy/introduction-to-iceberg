#!/bin/bash
# Idempotent schema bootstrap for the Hive Metastore.
#
# The stock /entrypoint.sh runs `schematool -initSchema` unconditionally, which
# fails (and kills the container) on every start after the first, because the
# schema already exists in PostgreSQL. This wrapper probes the schema first and
# tells the stock entrypoint to skip initialization when it's already there.
if "$HIVE_HOME"/bin/schematool -dbType "${DB_DRIVER:-postgres}" -info >/dev/null 2>&1; then
  echo "Metastore schema already present — skipping initialization."
  export IS_RESUME=true
else
  echo "No metastore schema found — initializing."
  export IS_RESUME=false
fi

exec /entrypoint.sh
