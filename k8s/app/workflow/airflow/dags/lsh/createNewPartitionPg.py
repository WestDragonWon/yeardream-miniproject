from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(dag_id='create_hourly_partitions_pg',
         default_args=default_args,
         schedule_interval='30 23 * * *',
         start_date=datetime(2024, 10, 4),
         catchup=False) as dag:

    create_partitions = PostgresOperator(
        task_id='create_hourly_partitions_for_tomorrow',
        postgres_conn_id='postgres_conn_id',
        sql="SELECT create_hourly_partitions_for_tomorrow();"
    )
    
    create_partitions


'''
CREATE OR REPLACE FUNCTION create_hourly_partitions_for_tomorrow() RETURNS void LANGUAGE plpgsql AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    partition_name TEXT;
BEGIN
    start_time := date_trunc('day', now() + INTERVAL '1 day'); -- Midnight of tomorrow
    end_time := start_time + INTERVAL '1 day'; -- Midnight the next day (24 hours)

    -- Loop to create hourly partitions
    WHILE start_time < end_time LOOP
        partition_name := 'iris_data_json_' || to_char(start_time, 'YYYYMMDD_HH24');
        
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS %I PARTITION OF iris_data_json
            FOR VALUES FROM (''%s'') TO (''%s'')
        ', partition_name, start_time, start_time + INTERVAL '1 hour');
        
        start_time := start_time + INTERVAL '1 hour';
    END LOOP;
END;
$$;

airflow connections add 'postgres_conn_id' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema 's32db' \
    --conn-login "$POSTGRES_USER" \
    --conn-password "$POSTGRES_PASSWORD" \
    --conn-port '5432'

'''