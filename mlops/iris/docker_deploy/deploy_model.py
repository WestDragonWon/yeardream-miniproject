from flask import Flask, request, jsonify
import mlflow.pyfunc
import pandas as pd
import numpy as np

app = Flask(__name__)

mlflow.set_tracking_uri("http://mlflow:8080")

model_name = "iris_model_final"
model_version = "production"



model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")

print(model)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # JSON 요청에서 데이터를 추출
        data = request.get_json(force=True)

        # DataFrame으로 변환 (입력된 데이터가 딕셔너리 형태일 경우)
        input_data = pd.DataFrame(data)

        # 모델 예측
        predictions = model.predict(input_data)

        # 결과 반환
        return jsonify({'predictions': predictions.tolist()})
    
    except Exception as e:
        return jsonify({'error': str(e)})

# 메인 실행 함수
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
