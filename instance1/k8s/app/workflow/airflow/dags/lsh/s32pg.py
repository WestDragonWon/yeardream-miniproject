from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
import pandas as pd
import boto3
from sqlalchemy import create_engine
import os
import io
import pyarrow.parquet as pq
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# S3 and PostgreSQL configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_REGION = 'ap-northeast-2'
bucket_name = 'team06-rawdata'
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = 'postgres'
db_port = '5432'
db_name = 's32db'

# Function to read S3 and store data in PostgreSQL
def read_s3_and_store_to_postgres():
    # Get current datetime for folder structure
    current_datetime = datetime.now()
    year = current_datetime.year
    month = current_datetime.month
    day = current_datetime.day
    hour = current_datetime.hour
    
    # Construct S3 folder path dynamically
    s3_folder_path = f'/iris-data/Your={year}/month={month}/day={day}/hour={hour}/'
    s3_object_pattern = f'{s3_folder_path}iris*.parquet'  # Adjust the file pattern if needed
    
    # AWS S3 client
    s3 = boto3.client('s3', 
                      region_name=S3_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    # Get a list of files matching the pattern from S3
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder_path)
    if 'Contents' not in response:
        print(f"No files found in {s3_folder_path}")
        return
    
    # SQLAlchemy engine for PostgreSQL
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
    # Loop through the files in the folder
    for obj in response['Contents']:
        s3_key = obj['Key']
        if s3_object_pattern in s3_key:
            parquet_obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
            body = parquet_obj['Body'].read()
            
            # Convert to pandas DataFrame
            data = pq.read_table(io.BytesIO(body)).to_pandas()
            
            # Store the DataFrame to PostgreSQL, append to table
            data.to_sql('iris_data', engine, if_exists='append', index=False)
            print(f"Data from {s3_key} has been appended to PostgreSQL.")

# Function to load data from PostgreSQL and train a model
# def load_data_and_train_model():
#     # Create PostgreSQL engine
#     engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    
#     # Load data from PostgreSQL
#     iris_data = pd.read_sql('SELECT * FROM iris_data', engine)

#     # Split data into features and labels
#     X = iris_data.drop(columns='Species')
#     y = iris_data['Species']
    
#     # Split into train and test sets
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Start MLflow tracking
#     mlflow.set_tracking_uri("http://mlflow:8080")
#     mlflow.set_experiment("testjun")

#     # Log the model training process
#     with mlflow.start_run():
#         model = RandomForestClassifier(n_estimators=100)
#         model.fit(X_train, y_train)
        
#         # Log the model to MLflow
#         mlflow.sklearn.log_model(model, "iris_model")
#         mlflow.register_model(f"runs:/{mlflow.active_run().info.run_id}/iris_model", "IrisModel")

#     print("Model has been trained and logged to MLflow.")

def reset_table():
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
    with engine.connect() as conn:
        conn.execute("DROP TABLE IF EXISTS iris_data CASCADE;")
        conn.execute("""
            CREATE TABLE iris_data (
                id SERIAL PRIMARY KEY,
                sepal_length FLOAT,
                sepal_width FLOAT,
                petal_length FLOAT,
                petal_width FLOAT,
                species VARCHAR(50),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            ) PARTITION BY RANGE (created_at);
        """)
    print("Table has been reset.")



# Airflow DAG definition
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 26),
    'retries': 1,
}

dag = DAG('iris_s3_pg', default_args=default_args, schedule_interval='@daily')

# Define tasks
task_read_s3_and_store_to_postgres = PythonOperator(
    task_id='read_s3_and_store_to_postgres',
    python_callable=read_s3_and_store_to_postgres,
    dag=dag,
)

# task_load_data_and_train_model = PythonOperator(
#     task_id='load_data_and_train_model',
#     python_callable=load_data_and_train_model,
#     dag=dag,
# )

task_reset_table = PythonOperator(
    task_id='reset_table',
    python_callable=reset_table,
    dag=dag,
)

# Task dependencies
task_reset_table >> task_read_s3_and_store_to_postgres 