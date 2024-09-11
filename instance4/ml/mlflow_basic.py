from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import mlflow
import mlflow.sklearn

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

from sklearn.metrics import accuracy_score

from mlflow.tracking import MlflowClient


iris = load_iris() # 꽃 받침과 꽃 잎 사이즈를 가지고 꽃의 종류를 결정

X = iris.data
y = iris.target

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 학습 데이터와 테스트 데이터로 분리 => train_test_split()
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=123)

mlflow.set_tracking_uri("http://127.0.0.1:5000") # dev.fastcampus.com:5000
print("Tracking URI : ", mlflow.get_tracking_uri())

exp = mlflow.set_experiment(experiment_name='iris_classification_experiments')

models = {
    "LogisticRegression" : LogisticRegression(
        max_iter=200, # 최대 반복 횟수
        C=0.5, # 규제 강도(C값이 작을수록 규제가 강해짐)
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

# 전체 모델에 대해서 기록을 하고 싶은데?
for model_name, model in models.items():
    with mlflow.start_run(run_name=model_name, nested=True) as run:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model_name = model_name
            best_model = model
            best_run_id = run.info.run_id  # 현재 run의 ID 저장
            best_experiment_id = run.info.experiment_id  # 현재 experiment ID 저장

        # 모델을 mlflow에 저장
        model_path = f"{model_name}_model"
        mlflow.sklearn.log_model(model, model_path) # 모델을 artifact 디렉토리에 저장

        mlflow.log_param(f'{model_name}_param', model.get_params()) # 파라미터 로그
        mlflow.log_metric(f'{model_name}_accuracy', accuracy) # 메트릭 로그

        print(f"Model Name: {model_name}, Accuracy: {accuracy}")


client = MlflowClient()


# 모델을 등록하고, 해당 모델의 버전을 반환
def register_model(model_name, run_id, accuracy, model_uri='model'): # 모델 등록
    model_uri = f"runs:/{run_id}/{model_uri}"
    model_version = mlflow.register_model(model_uri, model_name, tags = {'stage':'staging', 'accuracy':f"{accuracy:0.5f}"})
    return model_version

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



run_id = best_run_id
model_name = best_model_name
accuracy = best_accuracy



model_version = register_model(model_name, run_id, accuracy)
print(model_version)