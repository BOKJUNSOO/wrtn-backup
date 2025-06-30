from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id='crawler_dag',
    description='run container with DockerOperator',
    schedule='0 0 * * *',
    start_date=pendulum.datetime(2025,6,29, tz='Asia/Seoul'),
    catchup=False
) as dag :

    run_container = DockerOperator(
        task_id='run_container',
        image='crack_image:v1.0.0',
        container_name='crawler',
        command='python3 spider.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge'
    )

    run_container