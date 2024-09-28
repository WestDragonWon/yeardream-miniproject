from flask import Flask, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest
import requests
import os

app = Flask(__name__)

# Prometheus 메트릭 정의
registry = CollectorRegistry()
mlflow_metric = Gauge('mlflow_metric', 'Description of MLflow metric', ['metric_name'], registry=registry)

# MLflow 서버 URL
mlflow_server_url = os.getenv('MLFLOW_SERVER_URL', 'http://mlflow:8080')

def collect_metrics():
    # MLflow API에서 메트릭 수집
    try:
        response = requests.get(f"{mlflow_server_url}/api/2.0/mlflow/metrics")
        if response.status_code == 200:
            metrics = response.json().get('metrics', [])
            for metric in metrics:
                mlflow_metric.labels(metric['key']).set(metric['value'])
    except Exception as e:
        print(f"Error collecting metrics: {e}")

@app.route('/metrics')
def metrics():
    collect_metrics()
    return Response(generate_latest(registry), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9100)
