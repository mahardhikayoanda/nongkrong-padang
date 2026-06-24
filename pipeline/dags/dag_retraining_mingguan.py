from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Pengaturan default untuk DAG
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 16),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Mendefinisikan DAG
with DAG(
    'retraining_mingguan_dan_update_profil',
    default_args=default_args,
    description='DAG untuk fine-tuning model ABSA dan update vektor representasi pengguna ke PostgreSQL',
    schedule_interval='@weekly', # Dijalankan secara otomatis setiap minggu
    catchup=False,
    tags=['machine_learning', 'recsys'],
) as dag:

    # Task 1: Menjalankan skrip retraining untuk model ATE dan ASC
    # Pastikan path '/opt/airflow/...' disesuaikan dengan volume mapping di docker-compose.yml Anda
    task_retraining = BashOperator(
        task_id='retraining_model_absa',
        bash_command='python /opt/airflow/ml_model/src/trainer_ate.py && python /opt/airflow/ml_model/src/trainer_asc.py'
    )

    # Task 2: Memperbarui vektor profil berdasarkan hasil ekstraksi sentimen terbaru
    task_update_vektor = BashOperator(
        task_id='update_vektor_profil',
        bash_command='python /opt/airflow/ml_model/inference/update_vektor.py'
    )

    # Mengatur alur dependensi (Pipeline)
    # Vektor profil hanya akan diperbarui SETELAH model selesai di-retrain
    task_retraining >> task_update_vektor