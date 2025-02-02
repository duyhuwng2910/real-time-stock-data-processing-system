FROM bitnami/spark:latest

USER root

RUN apt-get update && apt-get install -y python3-pip

RUN pip install pandas cassandra-driver pyarrow

#RUN install_packages curl
#
#RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.1/spark-sql-kafka-0-10_2.12-3.5.1.jar --output /opt/bitnami/spark/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka-0-10_2.12/3.5.1/spark-streaming-kafka-0-10_2.12-3.5.1.jar --output /opt/bitnami/spark/jars/spark-streaming-kafka-0-10_2.12-3.5.1.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.5.0/spark-cassandra-connector_2.12-3.5.0.jar --output /opt/bitnami/spark/jars/spark-cassandra-connector_2.12-3.5.0.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.1/spark-token-provider-kafka-0-10_2.12-3.5.1.jar --output /opt/bitnami/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar --output /opt/bitnami/spark/jars/kafka-clients-3.4.1.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.4/hadoop-client-runtime-3.3.4.jar --output /opt/bitnami/spark/jars/hadoop-client-runtime-3.3.4.jar
#
#RUN curl https://repo1.maven.org/maven2/org/lz4/lz4-java/1.8.0/lz4-java-1.8.0.jar --output /opt/bitnami/spark/jars/lz4-java-1.8.0.jar
#
#RUN curl https://repo1.maven.org/maven2/org/xerial/snappy/snappy-java/1.1.10.3/snappy-java-1.1.10.3.jar --output /opt/bitnami/spark/jars/snappy-java-1.1.10.3.jar
#
#RUN curl https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.7/slf4j-api-2.0.7.jar --output /opt/bitnami/spark/jars/slf4j-api-2.0.7.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.4/hadoop-client-api-3.3.4.jar --output /opt/bitnami/spark/jars/hadoop-client-api-3.3.4.jar
#
#RUN curl https://repo1.maven.org/maven2/commons-logging/commons-logging/1.1.3/commons-logging-1.1.3.jar --output /opt/bitnami/spark/jars/commons-logging-1.1.3.jar
#
#RUN curl https://repo1.maven.org/maven2/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar --output /opt/bitnami/spark/jars/jsr305-3.0.2.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar --output /opt/bitnami/spark/jars/commons-pool2-2.11.1.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-driver_2.12/3.5.0/spark-cassandra-connector-driver_2.12-3.5.0.jar --output /opt/bitnami/spark/jars/spark-cassandra-connector-driver_2.12-3.5.0.jar
#
#RUN curl https://repo1.maven.org/maven2/org/scala-lang/modules/scala-collection-compat_2.12/2.11.0/scala-collection-compat_2.12-2.11.0.jar --output /opt/bitnami/spark/jars/scala-collection-compat_2.12-2.11.0.jar
#
#RUN curl https://repo1.maven.org/maven2/org/scala-lang/scala-reflect/2.12.11/scala-reflect-2.12.11.jar --output /opt/bitnami/spark/jars/scala-reflect-2.12.11.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/oss/java-driver-core-shaded/4.13.0/java-driver-core-shaded-4.13.0.jar --output /opt/bitnami/spark/jars/java-driver-core-shaded-4.13.0.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/oss/native-protocol/1.5.0/native-protocol-1.5.0.jar --output /opt/bitnami/spark/jars/native-protocol-1.5.0.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/oss/java-driver-shaded-guava/25.1-jre-graal-sub-1/java-driver-shaded-guava-25.1-jre-graal-sub-1.jar --output /opt/bitnami/spark/jars/java-driver-shaded-guava-25.1-jre-graal-sub-1.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/oss/java-driver-mapper-runtime/4.13.0/java-driver-mapper-runtime-4.13.0.jar --output /opt/bitnami/spark/jars/java-driver-mapper-runtime-4.13.0.jar
#
#RUN curl https://repo1.maven.org/maven2/com/datastax/oss/java-driver-query-builder/4.13.0/java-driver-query-builder-4.13.0.jar --output /opt/bitnami/spark/jars/java-driver-query-builder-4.13.0.jar
#
#RUN curl https://repo1.maven.org/maven2/com/typesafe/config/1.4.1/config-1.4.1.jar --output /opt/bitnami/spark/jars/config-1.4.1.jar
#
#RUN curl https://repo1.maven.org/maven2/io/dropwizard/metrics/metrics-core/4.1.18/metrics-core-4.1.18.jar --output /opt/bitnami/spark/jars/metrics-core-4.1.18.jar
#
#RUN curl https://repo1.maven.org/maven2/org/hdrhistogram/HdrHistogram/2.1.12/HdrHistogram-2.1.12.jar --output /opt/bitnami/spark/jars/HdrHistogram-2.1.12.jar
#
#RUN curl https://repo1.maven.org/maven2/org/reactivestreams/reactive-streams/1.0.3/reactive-streams-1.0.3.jar --output /opt/bitnami/spark/jars/reactive-streams-1.0.3.jar
#
#RUN curl https://repo1.maven.org/maven2/com/github/stephenc/jcip/jcip-annotations/1.0-1/jcip-annotations-1.0-1.jar --output /opt/bitnami/spark/jars/jcip-annotations-1.0-1.jar
#
#RUN curl https://repo1.maven.org/maven2/com/github/spotbugs/spotbugs-annotations/3.1.12/spotbugs-annotations-3.1.12.jar --output /opt/bitnami/spark/jars/spotbugs-annotations-3.1.12.jar
#
#RUN curl https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.10/commons-lang3-3.10.jar --output /opt/bitnami/spark/jars/commons-lang3-3.10.jar
#
#RUN curl https://repo1.maven.org/maven2/com/thoughtworks/paranamer/paranamer/2.8/paranamer-2.8.jar --output /opt/bitnami/spark/jars/paranamer-2.8.jar

COPY /jars /opt/bitnami/spark/jars

COPY conf/metrics-graphite.properties /opt/bitnami/spark/conf/metrics.properties

COPY conf/spark-defaults.conf /opt/bitnami/spark/conf/spark-defaults.conf

ENV SPARK_METRICS_ENABLED=true

ENV SPARK_UI_PROMETHEUS_ENABLED=true