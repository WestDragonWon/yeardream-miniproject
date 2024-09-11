from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import numpy as np
from sklearn.datasets import load_iris

app = FastAPI()

# MLflow tracking URI 및 실험 설정
mlflow.set_tracking_uri("http://192.168.88.209:8080")
mlflow.set_experiment("testjun")

# MLflow에서 모델 로드
model_uri = "runs:/2a5e08bd90f84d819e1ef4adb5ac8bee/iris_model"  # 실제 run_id로 변경 필요
model = mlflow.pyfunc.load_model(model_uri)

# Iris 데이터셋에서 species 이름 가져오기
iris = load_iris()
species_names = iris.target_names

class InputData(BaseModel):
    features: list

@app.post("/predict")
def predict(data: InputData):
    try:
        # 입력 데이터 형태 변경
        features = np.array(data.features).reshape(1, -1)
        
        # 예측 수행
        prediction = model.predict(features)
        
        # 결과 반환
        return {
            "prediction": int(prediction[0]),
            "species": species_names[int(prediction[0])]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail="잘못된 입력 데이터입니다. 입력을 확인하세요.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
