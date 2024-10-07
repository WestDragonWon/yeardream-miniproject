#!/bin/bash

while true; do
    if [ "$POD_STATUS_1" == "Failed" ] || [ "$POD_STATUS_1" == "Unknown" ] || [ -z "$POD_STATUS_1" ]; then
        nohup $SPARK_HOME/bin/spark-submit \
          --master k8s://https://master:6443/ \
          --deploy-mode cluster \
          --name 'consumertest' \
          --conf spark.executor.instances=3 \
          --conf spark.kubernetes.container.image=westdragonwon/sparkstreaming:1.11 \
          --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
          --conf "spark.kubernetes.driver.label.app=consumer-kafka-s3" \
          --conf "spark.kubernetes.executor.label.app=consumer-kafka-s3" \
          --packages org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901 \
          --conf spark.hadoop.fs.s3a.aws.credentials.provider=com.amazonaws.auth.EnvironmentVariableCredentialsProvider \
          --conf spark.driver.extraJavaOptions="-Divy.cache.dir=/tmp -Divy.home=/tmp" \
          --conf "spark.hadoop.fs.s3a.access.key=$(kubectl get secret workflow -o jsonpath="{.data.AWS_ACCESS_KEY_ID}" | base64 --decode)" \
          --conf "spark.hadoop.fs.s3a.secret.key=$(kubectl get secret workflow -o jsonpath="{.data.AWS_SECRET_ACCESS_KEY}" | base64 --decode)" \
          --conf spark.kubernetes.executor.deleteOnTermination=true \
          --conf "spark.eventLog.enabled=true" \
          --conf "spark.eventLog.dir=file:/mnt/spark-history-logs" \
          --conf spark.kubernetes.driver.podTemplateFile=$SPARK_HOME/podtemplate/driver-pod-template.yaml \
          --conf spark.kubernetes.executor.podTemplateFile=$SPARK_HOME/podtemplate/executor-pod-template.yaml \
          local:///opt/spark/jobs/consumer-kafka-s3.py > spark_job-1.log 2>&1 &
    fi
    sleep 60
done
