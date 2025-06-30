from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
import pendulum


with DAG(
    dag_id='crawler_dag',
    description='run container with DockerOperator',
    schedule='0 0 * * *',
    start_date=pendulum.datetime(2025,6,29, tz='Asia/Seoul'),
    catchup=False
) as dag :

    run_container = DockerOperator(
        task_id='run_container',
        image='crack_images:latest',
        command='python spider.py',
        docker_url="unix:///var/run/docker.sock",
        network_mode='crack',
        auto_remove=True,
        mount_tmp_dir=False,
    )

    run_container