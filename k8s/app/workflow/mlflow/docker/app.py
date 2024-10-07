import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# MLflow tracking URI 및 실험 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")  # 서비스 클러스터 IP
mlflow.set_experiment("iris_classification_experiments")  # 실험 이름으로 변경

class InputData(BaseModel):
    input_model_name: str  # 모델 이름 추가
    features: list[float]  # features를 float 타입의 리스트로 설정

def get_production_model(name: str):
    client = mlflow.tracking.MlflowClient()
    model_version = client.get_registered_model(name)
    
    # 'Production' 태그가 있는 모델을 반환
    for v in model_version.latest_versions:
        if v.current_stage == "Production":  # 스테이지가 'Production'인지 확인
            return v
    return None

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"}

@app.post("/predict")
def predict(data: InputData):
    logger.info(f"Received input: {data}")  # 입력 데이터 로깅
    try:
        # 입력 피처 수 검증
        if len(data.features) != 4:  # Iris 데이터셋의 경우
            raise ValueError("features는 정확히 4개의 요소를 가져야 합니다.")

        model_version = get_production_model(data.input_model_name)
        
        if model_version is None:
            logger.error(f"Model '{data.input_model_name}' in production not found.")
            raise HTTPException(status_code=404, detail=f"Model '{data.input_model_name}' in production not found.")
        
        model_uri = f"models:/{data.input_model_name}/{model_version.version}"  # 'Production' 모델 로드
        model = mlflow.pyfunc.load_model(model_uri)
        
        features = np.array(data.features).reshape(1, -1)
        
        logger.info(f"Features reshaped for prediction: {features}")  # 특성 데이터 로깅
        prediction = model.predict(features)
        
        return {
            "prediction": prediction[0]  # 예측 결과를 문자열로 반환
        }
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")  # ValueError 로깅
        raise HTTPException(status_code=400, detail="잘못된 입력 데이터입니다. 입력을 확인하세요.")
    except Exception as e:
        logger.error(f"Internal Server Error: {str(e)}")  # 일반적인 예외 로깅
        raise HTTPException(status_code=500, detail=str(e))
