# dags

## dataflow_v1


1. 별도의 전처리가 되지 않은 csv 파일을 s3 저장소에서 postgres로 전송

2. postgres로 적재된 데이터를 이용하여 모델로 훈련시킴

3. 훈련된 모델 중 가장 예측치가 높은 모델의 stage를 production으로 등록

4. 등록된 모델을 fastapi에서 가져다 쓰게하고 모델 예측 실험 가능