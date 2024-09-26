helm install spark-operator bitnami/spark --namespace default

kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/spark-on-k8s-operator/master/manifests/crds/sparkoperator.k8s.io_sparkapplications.yaml
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/spark-on-k8s-operator/master/manifests/crds/sparkoperator.k8s.io_scheduledsparkapplications.yaml
