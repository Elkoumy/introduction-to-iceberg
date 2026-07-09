# Spark 3.5 + Jupyter image for the Iceberg bootcamp.
#
# Extends the official Jupyter PySpark image (Spark 3.5.0 / Scala 2.12 /
# Hadoop 3.3.4) by pre-downloading the Iceberg, S3 and PostgreSQL JARs into a
# shared Ivy cache. spark-defaults.conf points spark.jars.ivy at this cache,
# so the first SparkSession in class starts instantly and works offline.
FROM jupyter/pyspark-notebook:spark-3.5.0

USER root

ENV IVY_DIR=/opt/ivy2

# Resolve the exact same coordinates listed in spark-defaults.conf.
# spark-submit downloads them (plus transitive deps) into ${IVY_DIR} at build
# time; the trivial app just proves resolution succeeded.
RUN echo "print('Iceberg JARs resolved into the Ivy cache')" > /tmp/warm.py && \
    spark-submit \
      --conf spark.jars.ivy=${IVY_DIR} \
      --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.2,org.apache.iceberg:iceberg-aws-bundle:1.5.2,org.apache.hadoop:hadoop-aws:3.3.4,org.postgresql:postgresql:42.6.0 \
      /tmp/warm.py && \
    rm /tmp/warm.py && \
    chown -R ${NB_UID}:${NB_GID} ${IVY_DIR}

USER ${NB_UID}

# Python client for querying Trino from notebooks (Lab 3+)
RUN pip install --no-cache-dir trino==0.328.0

WORKDIR /home/jovyan/notebooks
