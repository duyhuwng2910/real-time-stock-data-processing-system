### Dockerfile dùng để tích hợp file jar vào cassandra image, 
### phục vụ cho việc giám sát hiệu năng của Cassandra container

FROM cassandra

# install curl
RUN apt-get update && apt-get install -y curl

ADD https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar /usr/local/lib/jmx_prometheus_javaagent.jar

COPY cassandra.yml /usr/local/etc/cassandra.yml

COPY cassandra.yaml /etc/cassandra/cassandra.yaml

RUN chmod a+r /usr/local/lib/jmx_prometheus_javaagent.jar

RUN echo 'JVM_OPTS="$JVM_OPTS -javaagent:/usr/local/lib/jmx_prometheus_javaagent.jar=7070:/usr/local/etc/cassandra.yml"' >>  /etc/cassandra/cassandra-env.sh