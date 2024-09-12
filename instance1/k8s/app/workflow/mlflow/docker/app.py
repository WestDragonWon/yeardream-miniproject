from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import numpy as np
from sklearn.datasets import load_iris

app = FastAPI()

# MLflow에서 모델 로드
model_uri = "runs:/c2135c3fb3804016bb75ab9ca6e6d62c/iris_model"  # 자동화를 위해 
model = mlflow.pyfunc.load_model(model_uri)

# Iris 데이터셋에서 species 이름 가져오기
iris = load_iris()
species_names = iris.target_names

class InputData(BaseModel):
    model_name: str  # 모델 이름 추가
    version: int     # 모델 버전 추가
    features: list

@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

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
