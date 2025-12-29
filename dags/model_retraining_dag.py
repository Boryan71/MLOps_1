from airflow import DAG
from datetime import timedelta, datetime
from airflow.operators.python import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='model_retraining_dag',
    schedule_interval='@weekly',  # Еженедельно проверяем дрифт данных
    start_date=datetime(2025, 12, 1),
    catchup=False,
    default_args=default_args,
) as dag:

    # Task для проверки дрифта данных
    def check_data_drift():
        response = requests.get("http://app:8000/check-data-drift/")
        data_drift = response.json()["data_drift"]
        return data_drift

    # Task для переобучения модели
    def retrain_model_if_needed(**context):
        # Получаем результат из предыдущей задачи
        drift_share = context['ti'].xcom_pull(task_ids='check_data_drift')

        if drift_share > 0.5:
            requests.get("http://app:8000/retrain-model/")
            return "Model retrained due to significant data drift!"
        else:
            return "No significant data drift detected."

    # Airflow tasks
    check_drift_task = PythonOperator(
        task_id='check_data_drift',
        python_callable=check_data_drift,
        do_xcom_push=True,
    )

    retrain_model_task = PythonOperator(
        task_id='retrain_model_if_needed',
        python_callable=retrain_model_if_needed,
        provide_context=True,
    )

    # Dependency chain
    check_drift_task >> retrain_model_task