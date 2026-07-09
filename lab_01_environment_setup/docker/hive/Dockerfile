# Hive Metastore 3.1.3 for the Iceberg bootcamp.
#
# The stock apache/hive image cannot talk to PostgreSQL or S3, so we add:
#   - postgresql JDBC driver          (metastore schema lives in Postgres)
#   - hadoop-aws + aws-java-sdk       (warehouse dir is s3a://warehouse/ on MinIO)
#
# JAR versions are pinned to the Hadoop bundled in this image (3.1.0) —
# hadoop-aws must match hadoop-common exactly, and 3.1.0 was built against
# aws-java-sdk-bundle 1.11.271.
FROM apache/hive:3.1.3

ADD --chown=hive:hive https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar /opt/hive/lib/
ADD --chown=hive:hive https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.1.0/hadoop-aws-3.1.0.jar /opt/hive/lib/
ADD --chown=hive:hive https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.271/aws-java-sdk-bundle-1.11.271.jar /opt/hive/lib/

COPY --chown=hive:hive hive-site.xml /opt/hive/conf/hive-site.xml

# Stock entrypoint fails on restart (re-runs initSchema); wrap it to make
# schema initialization idempotent.
COPY --chown=hive:hive --chmod=755 entrypoint-wrapper.sh /entrypoint-wrapper.sh
ENTRYPOINT ["/entrypoint-wrapper.sh"]
