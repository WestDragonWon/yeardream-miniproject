from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import numpy as np

app = FastAPI()

# MLflow tracking URI 및 실험 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")  # 서비스 클러스터 IP
mlflow.set_experiment("testjun")  # 실험 이름으로 변경

class InputData(BaseModel):
    model_name: str  # 모델 이름 추가
    version: int     # 모델 버전 추가
    features: list

@app.get("/health")
def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy"}

def get_production_model(name: str):
    client = mlflow.tracking.MlflowClient()
    
    # "production" 태그가 있는 모델 검색
    registered_models = client.search_registered_models(
        filter_string=f'tags.production = "true" and name = "{name}"'
    )
    
    return registered_models[0] if registered_models else None

@app.post("/predict")
def predict(data: InputData):
    try:
        # "production" 태그가 있는 모델 검색
        production_model = get_production_model(data.model_name)
        
        if production_model is None:
            raise HTTPException(status_code=404, detail="Production model not found.")
        
        # 모델 URI 설정 (모델 이름과 버전)
        model_uri = f"models:/{production_model.name}/{data.version}"  # 동적으로 모델 URI 생성
        model = mlflow.pyfunc.load_model(model_uri)  # 모델 로드
        
        # 입력 데이터 형태 변경
        features = np.array(data.features).reshape(1, -1)
        
        # 예측 수행
        prediction = model.predict(features)
        
        # 결과 반환
        return {
            "prediction": int(prediction[0])
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="잘못된 입력 데이터입니다. 입력을 확인하세요.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
