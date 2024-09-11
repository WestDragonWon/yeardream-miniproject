# 접속 아이피

http://<EC2 퍼블릭 IP>:30003


# mlflow - DB 연결 확인
- testyong.py 실행해서 데이터가 제대로 적재 되는지 확인

# mlflow - DB 연결 확인
- testyong.py 실행해서 데이터가 제대로 적재 되는지 확인

# 머신러닝 모델 FastAPI에 서빙

1. 모델의 Run ID를 FastAPI 앱을 구성할 코드에 작성해야함.

2. FastAPI앱에 MLflow tracking URI와 실험 설정을 꼭 작성해야함.

3. http://ec2_public_ip:8000/docs로 들어가서 /predict 부분을 클릭하면 나오는 try it out 버튼을 클릭

4. 생성된 창에 피쳐를 입력해주고 아래 Execute 버튼을 눌려주면 결과가 나온다.