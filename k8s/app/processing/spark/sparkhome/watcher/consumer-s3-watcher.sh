#!/bin/bash

cleanup_pods() {
    local APP_NAME=$1
    local POD_STATUS=$2
    
    if [ "$POD_STATUS" == "Failed" ] || [ "$POD_STATUS" == "Unknown" ]; then
        echo "Cleaning up $APP_NAME pods in $POD_STATUS state..."
        # Delete pods with the specific app label in Failed or Unknown state
        kubectl delete pod -l app=$APP_NAME 
        # Wait for pod deletion to complete
        sleep 10
    fi
}

submit_spark_job() {
    local APP_NAME=$1
    local PYTHON_FILE=$2

    nohup $SPARK_HOME/bin/spark-submit \
      --master k8s://https://master:6443/ \
      --deploy-mode cluster \
      --name $APP_NAME \
      --conf spark.executor.instances=3 \
      --conf spark.kubernetes.container.image=westdragonwon/sparkstreaming:1.11 \
      --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
      --conf "spark.kubernetes.driver.label.app=$APP_NAME" \
      --conf "spark.kubernetes.executor.label.app=$APP_NAME" \
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
      local:///opt/spark/jobs/$PYTHON_FILE > spark_job.log 2>&1 &
}

while true; do
    # Check and submit consumer-s3 job
    POD_STATUS_1=$(kubectl get pod -l app=consumer-s3 -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    if [ "$POD_STATUS_1" == "Failed" ] || [ "$POD_STATUS_1" == "Unknown" ] || [ -z "$POD_STATUS_1" ]; then
	cleanup_pods "consumer-s3" "$POD_STATUS_1"
        submit_spark_job "consumer-s3" "consumer-kafka-s3.py"
    fi

    # Check and submit sparkKafka2s3 job
    POD_STATUS_2=$(kubectl get pod -l app=iris-s3 -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
    if [ "$POD_STATUS_2" == "Failed" ] || [ "$POD_STATUS_2" == "Unknown" ] || [ -z "$POD_STATUS_2" ]; then
	cleanup_pods "iris-s3" "$POD_STATUS_2"
        submit_spark_job "iris-s3" "sparkKafka2s3.py"
    fi

    sleep 60
done
