import mlflow
import mlflow.sklearn
import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# PostgreSQL 접속 정보
db_user = 'mlops_user'      # PostgreSQL 사용자 이름
db_password = '1234'   # PostgreSQL 비밀번호
db_host = '192.168.189.70'          # Pod 이름
db_port = '5432'                # PostgreSQL 포트
db_name = 's32db'  # 데이터베이스 이름

# SQLAlchemy를 사용하여 PostgreSQL 엔진 생성
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Iris 데이터 읽기
iris_data = pd.read_sql('SELECT * FROM iris_data', engine)

# 특징(X)과 레이블(y) 분리
X = iris_data.drop(columns='Species')
y = iris_data['Species']  

# 훈련 데이터와 테스트 데이터로 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow 서버 URL 설정
mlflow.set_tracking_uri("http://10.103.73.87:8080")  # MLflow 서버 URL
mlflow.set_experiment("testjun")  # 실험 이름 설정

# MLflow 실행 시작
mlflow.start_run()

# 모델 훈련
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 모델 저장
model_path = "iris_model"
mlflow.sklearn.log_model(model, model_path)

# 모델 레지스트리에 등록
model_uri = f"runs:/{mlflow.active_run().info.run_id}/{model_path}"
mlflow.register_model(model_uri, "IrisModel")

# MLflow 실행 종료
mlflow.end_run()
