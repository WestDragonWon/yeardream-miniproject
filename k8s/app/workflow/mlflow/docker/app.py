from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import numpy as np

app = FastAPI()

# MLflow tracking URI 및 실험 설정
mlflow.set_tracking_uri("http://mlflow:8080")  # 서비스 클러스터 IP
mlflow.set_experiment("testjun")  # 실험 이름으로 변경

class InputData(BaseModel):
    input_model_name: str  # 모델 이름 추가
    version: int           # 모델 버전 추가
    features: list

def get_production_model(name: str):
    client = mlflow.tracking.MlflowClient()
    registered_models = client.search_registered_models(
        filter_string=f'tags.production = "true" and name = "{name}"'
    )
    return registered_models[0] if registered_models else None

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/predict")
def predict(data: InputData):
    try:
        production_model = get_production_model(data.input_model_name)
        
        if production_model is None:
            raise HTTPException(status_code=404, detail="Production model not found.")
        
        model_uri = f"models:/{production_model.name}/{data.version}"
        model = mlflow.pyfunc.load_model(model_uri)
        
        features = np.array(data.features).reshape(1, -1)
        
        prediction = model.predict(features)
        
        return {
            "prediction": int(prediction[0])
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 입력 데이터입니다. 입력을 확인하세요.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
