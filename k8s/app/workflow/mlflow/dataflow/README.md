# S3 2 DB 2 MLflow


## 목차

1. 개요
2. 실행환경
3. 코드 설명
4. 이슈

### 개요

이 시스템의 목적은 Amazon S3에 저장된 데이터를 데이터베이스로 전송하고, 이후 이 데이터를 MLflow로 전송하여 머신러닝 모델의 학습 및 실험을 관리하는 것임. 데이터 파이프라인의 효율성과 자동화를 위한 시스템.

### 실행환경

- 공통 환경

		Python 3.11.9
		Airflow 2.9.3
		boto3
		pandas
		mlflow
		scikit-learn

**postgres**

	SQLAlchemy

**redis**

	rediscluster



### 코드 설명

#### S3 ~ postgres ~ mlflow


		bucket_name = 'team06-mlflow-feature'
		s3_object_name = 'iris1.csv'

- bucket_name에 s3에 저장된 데이터 버킷 이름 설정
- s3_object_name 읽어올 파일을 입력

		AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
		AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
		S3_REGION = 'ap-northeast-2'

- AWS에 접근하기 위한 자격 증명을 환경 변수에서 가져옴
- S3_REGION 리전 설정

		db_user = os.getenv("POSTGRES_USER")
		db_password = os.getenv("POSTGRES_PASSWORD")
		db_host = 'postgres'
		db_port = '5432'
		db_name = 's32db'

- 유저와 비밀번호는 환경변수에서 가져오게끔
- 서비스 이름, 포트, db 이름을 설정해줌

		def read_s3_and_store_to_postgres():
			# AWS 자격 증명으로 S3 클라이언트 생성
			s3 = boto3.client('s3', 
							region_name=S3_REGION,
							aws_access_key_id=AWS_ACCESS_KEY_ID,
							aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

			# S3에서 CSV 객체 가져오기
			csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
			body = csv_obj['Body'].read().decode('utf-8')

			# 파일 내용을 pandas DataFrame으로 변환
			data = pd.read_csv(io.StringIO(body), sep=';')

			# SQLAlchemy를 사용하여 PostgreSQL 엔진 생성
			engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

			# 데이터프레임을 PostgreSQL에 로드
			data.to_sql('iris_data', engine, if_exists='replace', index=True)
			print("Data has been loaded into PostgreSQL.")

- boto3 라이브러리를 사용하여 S3 클라이언트를 생성하고, 지정된 버킷과 파일 이름으로 CSV 파일을 가져옴

- 
CSV 파일의 내용을 pandas 데이터프레임으로 변환한 후, SQLAlchemy를 통해 PostgreSQL에 연결하여 데이터를 iris_data 테이블에 저장
		
		# Iris 데이터 읽기
		iris_data = pd.read_sql('SELECT * FROM iris_data', engine)

		# 특징(X)과 레이블(y) 분리
		X = iris_data.drop(columns='Species')
		y = iris_data['Species']  

		# 훈련 데이터와 테스트 데이터로 분리
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

		# MLflow 설정
		mlflow.set_tracking_uri("http://mlflow:8080")
		mlflow.set_experiment("testjun")

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

		print("Model has been trained and logged to MLflow.")

- PostgreSQL에서 iris_data 테이블의 데이터를 읽어옴

- 데이터를 특징(X)과 레이블(y)로 분리한 후, 훈련 데이터와 테스트 데이터로 나눔

- MLflow를 설정하고, 랜덤 포레스트 모델을 훈련시킨 뒤, 이걸 MLflow에 기록하고 레지스트리에 등록

		default_args = {
			'owner': 'airflow',
			'depends_on_past': False,
			'start_date': datetime(2023, 9, 26),
			'retries': 1,
		}

		dag = DAG('iris_model', default_args=default_args, schedule_interval='@daily')

		task_read_s3_and_store_to_postgres = PythonOperator(
			task_id='read_s3_and_store_to_postgres',
			python_callable=read_s3_and_store_to_postgres,
			dag=dag,
		)

		task_load_data_and_train_model = PythonOperator(
			task_id='load_data_and_train_model',
			python_callable=load_data_and_train_model,
			dag=dag,
		)

		task_read_s3_and_store_to_postgres >> task_load_data_and_train_model

- default_args: DAG의 기본 인수들을 설정. 소유자, 과거 의존성, 시작 날짜, 재시도 수 등등

- dag: DAG를 정의하고, 매일 실행되도록 설정

- PythonOperator: 두 개의 작업을 정의. 하나는 S3에서 데이터를 읽고 PostgreSQL에 저장하는 작업, 다른 하나는 데이터를 읽어 모델을 훈련시키는 작업

- 마지막에 작업의 실행 순서를 정의함. 첫 번째 작업이 완료된 후 두 번째 작업이 실행된다는 뜻


#### S3 ~ redis ~ mlflow

- 버킷 이름, 파일 이름, aws 자격증명은 위 코드와 동일함.

	redis_host = 'redis-cluster'  # Redis 서비스 이름
	redis_port = '6379'

- Redis 클러스터의 호스트와 포트 설정


		def read_s3_and_store_to_redis():
			try:
				# Redis 클러스터 접속 정보
				startup_nodes = [{"host": redis_host, "port": redis_port}]
				redis_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

				# AWS 자격 증명으로 S3 클라이언트 생성
				s3 = boto3.client('s3', 
								region_name=S3_REGION,
								aws_access_key_id=AWS_ACCESS_KEY_ID,
								aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

				# S3에서 CSV 객체 가져오기
				csv_obj = s3.get_object(Bucket=bucket_name, Key=s3_object_name)
				body = csv_obj['Body'].read().decode('utf-8')
				data = pd.read_csv(StringIO(body))

				for index, row in data.iterrows():
					redis_client.set(f"row:{index}", json.dumps(row.to_dict()))

				print("Data has been imported to Redis.")
			except Exception as e:
				print(f"Error reading from S3 or storing to Redis: {e}")

- Redis 클라이언트 생성: Redis 클러스터에 연결

- S3 클라이언트 생성: AWS 자격 증명을 사용하여 S3 클라이언트 생성

- CSV 파일 읽기: S3에서 CSV 파일을 가져와 내용을 읽고 pandas 데이터프레임으로 변환

- Redis에 저장: 각 행을 JSON 형식으로 변환하여 Redis에 저장. 키는 row:{index} 형식

- 예외 처리: S3 읽기 또는 Redis 저장 중 오류가 발생하면 오류 메시지를 출력함

		def load_from_redis_and_train_model():
			# Redis 클러스터 접속 정보
			startup_nodes = [{"host": redis_host, "port": redis_port}]
			redis_client = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

			data = []
			index = 0

			try:
				while True:
					row = redis_client.get(f"row:{index}")
					if row is None:
						break
					data.append(json.loads(row))
					index += 1

				iris_data = pd.DataFrame(data)

				# MLflow 설정
				mlflow.set_tracking_uri("http://mlflow:8080")
				mlflow.set_experiment("iris_experiment")

				# MLflow 실행 시작
				mlflow.start_run()

				# 특징(X)과 레이블(y) 분리
				X = iris_data.drop(columns='Species')
				y = iris_data['Species']

				# 훈련 데이터와 테스트 데이터로 분리
				X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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

				print("Model has been trained and logged to MLflow.")
			except Exception as e:
				print(f"Error loading data from Redis or training model: {e}")

- Redis 클라이언트 생성: Redis 클러스터에 연결

- 데이터 불러오기: Redis에서 저장된 데이터를 반복적으로 가져와 리스트에 저장. row:{index} 형식의 키를 사용하여 데이터를 가져옴.

- 데이터프레임 생성: 가져온 데이터를 pandas 데이터프레임으로 변환

- MLflow 설정: MLflow 서버 URL과 실험 이름을 설정.

- 모델 훈련: 특징(X)과 레이블(y)을 분리한 후, 훈련 데이터와 테스트 데이터로 나누고, 랜덤 포레스트 모델을 훈련함

- 모델 저장: 훈련한 모델을 MLflow에 기록하고 레지스트리에 등록

- 마지막은 예외 처리: Redis에서 데이터 불러오기 또는 모델 훈련 중 오류나면 오류 메세지 출력

		default_args = {
			'owner': 'airflow',
			'depends_on_past': False,
			'start_date': datetime(2023, 9, 26),
			'retries': 1,
		}

		dag = DAG('redis', default_args=default_args, schedule_interval='@daily')

		task_read_s3_and_store_to_redis = PythonOperator(
			task_id='read_s3_and_store_to_redis',
			python_callable=read_s3_and_store_to_redis,
			dag=dag,
		)

		task_load_from_redis_and_train_model = PythonOperator(
			task_id='load_from_redis_and_train_model',
			python_callable=load_from_redis_and_train_model,
			dag=dag,
		)

		task_read_s3_and_store_to_redis >> task_load_from_redis_and_train_model

postgres의 경우와 동일함

### 이슈

1. 라이브러리 없음

사용하여는 라이브러리가 airflow에 있어야함. no module name~ 이라는 오류가 발생한다면, airflow 이미지를 빌드할때 필요 모듈들을 같이 넣어줘야함.

2. s3_object_name 경로

맨 앞에 /(루트) 경로를 입력하면 오류가 생김. 필요없으니 붙이지 말자.

3. SQLAlchemy

postgres의 경우 연결하기 위해선 엔진이 필요하다

SQLAlchemy의 create_engine을 이용하여 엔진을 생성해주자.

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')