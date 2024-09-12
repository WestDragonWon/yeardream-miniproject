from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import mlflow.pyfunc
import numpy as np

app = FastAPI()

# MLflow tracking URI 및 실험 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")  # service cluster ip
mlflow.set_experiment("testjun")  # 실험 이름으로 변경

class InputData(BaseModel):
    features: list

@app.post("/predict")
def predict(data: InputData):
    try:
        # 가장 최근 모델의 실행 ID 가져오기
        last_run_info = mlflow.search_runs(order_by=["start_time desc"], max_results=1)
        run_id = last_run_info.iloc[0].run_id  # 최근 실행 ID
        
        # 모델 URI 설정
        model_uri = f"runs:/{run_id}/model"  # 모델 URI 형식
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
