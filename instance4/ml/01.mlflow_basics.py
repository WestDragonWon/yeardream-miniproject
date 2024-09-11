from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import mlflow
import mlflow.sklearn

iris = load_iris() # 꽃 받침과 꽃 잎 사이즈를 가지고 꽃의 종류를 결정

X = iris.data
y = iris.target

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 학습 데이터와 테스트 데이터로 분리 => train_test_split()
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=123)


from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

model = LogisticRegression(max_iter=0)
model.fit(X_train, y_train) # train=모의고사 # 학습을 시킬 때는 학습 데이터만 제공

y_pred = model.predict(X_test) # 수능 문제를 제공
accuracy = accuracy_score(y_test, y_pred)

print(f"정확도 : {accuracy * 100}")

mlflow.set_tracking_uri("http://10.108.228.103:8080")
print("Tracking URI : ", mlflow.get_tracking_uri())

exp = mlflow.set_experiment(experiment_name='iris_classification_experiments')

print(f"Name: {exp.name}")
print(f"ID: {exp.experiment_id}")
print(f"Location: {exp.artifact_location}")
print(f"Tags: {exp.tags}")
print(f"Lifecycle: {exp.lifecycle_stage}")
print(f"Create Timestamp: {exp.creation_time}")

import time
time.time()

import mlflow.sklearn

mlflow.autolog()

mlflow.start_run(nested=True) # 실험 시작
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train) # train=모의고사 # 학습을 시킬 때는 학습 데이터만 제공

y_pred = model.predict(X_test) # 수능 문제를 제공
accuracy = accuracy_score(y_test, y_pred)

print(f"정확도 : {accuracy * 100}")

mlflow.end_run() # 실험 종료

import mlflow.sklearn

mlflow.autolog()

# with, end 구문을 붙이지 않아도 알아서 실험 종료가 됩니다.
with mlflow.start_run(nested=True): # 실험 시작
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train) # train=모의고사 # 학습을 시킬 때는 학습 데이터만 제공

    y_pred = model.predict(X_test) # 수능 문제를 제공
    accuracy = accuracy_score(y_test, y_pred)

    print(f"정확도 : {accuracy * 100}")

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

models = {
    "LogisticRegression" : LogisticRegression(
        max_iter=200, # 최대 반복 횟수
        C=1.0, # 규제 강도(C값이 작을수록 규제가 강해짐)
        solver='lbfgs', # 최적화 알고리즘
        random_state=123
    ),
    "RandomForest" : RandomForestClassifier(
        n_estimators=100, # 트리의 갯수
        max_depth=None,
        random_state=123
    ),
    "SVC" : SVC(
        kernel='linear', # linear, sigmoid, poly, rbf
        random_state=123
    )
}

mlflow.autolog()

best_accuracy = 0
best_model = None
best_model_name = None

with mlflow.start_run(nested=True):
    for model_name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model_name = model_name
            best_model = model

        print(f"Model Name: {model_name}, Accuracy: {accuracy}")

        mlflow.log_param('best_model', best_model_name) # 파라미터 로그
        mlflow.log_metric('best_accuracy', best_accuracy) # 메트릭 로그

    print(f"Best Model Name: {best_model_name}, Best Accuracy: {best_accuracy}")

mlflow.autolog()

# 전체 모델에 대해서 기록을 하고 싶은데?
for model_name, model in models.items():
    with mlflow.start_run(run_name=model_name, nested=True):
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        # 모델을 mlflow에 저장
        model_path = f"{model_name}_model"
        mlflow.sklearn.log_model(model, model_path) # 모델을 artifact 디렉토리에 저장

        mlflow.log_param(f'{model_name}_param', model.get_params()) # 파라미터 로그
        mlflow.log_metric(f'{model_name}_accuracy', accuracy) # 메트릭 로그

        print(f"Model Name: {model_name}, Accuracy: {accuracy}")

# 모델 관리
from mlflow.tracking import MlflowClient

client = MlflowClient()


# 모델을 등록하고, 해당 모델의 버전을 반환
def register_model(model_name, run_id, model_uri='model'): # 모델 등록
    model_uri = f"runs:/{run_id}/{model_uri}"
    model_version = mlflow.register_model(model_uri, model_name)
    return model_version

# 등록된 모델을 stage 단계로 승격
def promote_to_staging(model_name, run_id, model_uri): # stage
    model_version = register_model(model_name, run_id, model_uri)

    client.set_model_version_tag(
        name=model_name,
        version=model_version.version,
        key='stage',
        value='staging'
    )
    print(f"Model: {model_name}, version: {model_version} promoted to Staging...")

def promote_to_production(model_name, version): # production
    client.set_model_version_tag(
        name=model_name,
        version=version,
        key='stage',
        value='production'
    )

    print(f"Model: {model_name}, version: {version} promoted to Production...")


def archive_model(model_name, version): # archive: 모델 폐기 단계
    client.set_model_version_tag(
        name=model_name,
        version=version,
        key='stage',
        value='archived'
    )
    
    print(f"Model: {model_name}, version: {version} Archived ...")


'''
# http://127.0.0.1:5000/#/experiments/273063112817362178/runs/c43fcd5ca3e1413cbcd802d622f591e6
# 실험ID: 273063112817362178
# 실행ID: c43fcd5ca3e1413cbcd802d622f591e6
# Model Name: LogisticRegression

# (1) 모델 등록
run_id = 'c43fcd5ca3e1413cbcd802d622f591e6'
model_name = 'LogisticRegression'

model_version = register_model(model_name, run_id)
print(model_version)

# (2) 모델을 staging 단계로 승격
promote_to_staging(model_name, run_id, 'model')

# (3) 모델을 Production 단계로 승격
promote_to_production(model_name, '3')


# (4) 새로운 버전의 모델을 Production으로 승격시키고, 기존의 Production 버전은 Archived
promote_to_production(model_name, '4') # 4 staging -> production
archive_model(model_name, '3') # production -> archive
'''
