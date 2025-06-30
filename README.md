
# 프로젝트 구성

```Markdown
.
├── airflow/           # 에어플로우 인프라 구성
│   ├── dags/
│   ├── config/
│   ├── docker-compose.yaml
│   └── .env
│
├── docker/
│   ├── spider.py       # 원본 소스코드
│   ├── pyproject.toml  # 이미지 의존성 명시 파일
│   └── Dockerfile      # 이미지 빌드용 도커파일
│
└── README.md           # 프로젝트 설명
```
# 포트 정보

```
`airflow webserver` : `8080`포트
`postgres`          : `5432`포트
```

<br>

# 프로젝트 실행
## ✔ 도커 데스크탑 설치 (window)
- 아래에 링크에서 window 버전을 설치
```angular2html
https://docs.docker.com/desktop/setup/install/windows-install/
```
- 설치된 docker engine을 실행시킵니다.

<br>

## ✔ 도커 데스크탑 설치 (Linux apt)
- 리눅스 운영체제일 경우 `apt` 를 이용하여 설치 가능합니다.
- 설치전 실행
```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
- 패키지 다운로드
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
- 도커엔진 실행
```bash
sudo service docker start
```

<br>

## ✔ 컨테이너 빌드 (Airflow 컨테이너)
- `airflow` 디렉토리에서 다음 명령어를 통해 `airflow` 컨테이너를 빌드합니다.

```
docker-compose up -d
```

<br>

## ✔ DB 설정
- `postgres`의 `schema` ,`database` 설정을 해주어야 합니다.

1. 컨테이너명 확인
```angular2html
docker ps
```

2. 아래의 경우 `컨테이너명은` `3ef2c10e64c2` 입니다.
```log
CONTAINER ID   IMAGE                   COMMAND                   CREATED             STATUS                       PORTS                                         NAMES
326a5cc604fc   apache/airflow:2.10.3   "/usr/bin/dumb-init …"   About an hour ago   Up About an hour (healthy)   8080/tcp                                      airflow-airflow-triggerer-1
58a289587aa5   apache/airflow:2.10.3   "/usr/bin/dumb-init …"   About an hour ago   Up About an hour (healthy)   8080/tcp                                      airflow-airflow-scheduler-1
7599786bcea5   apache/airflow:2.10.3   "/usr/bin/dumb-init …"   About an hour ago   Up About an hour (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp   airflow-airflow-webserver-1
3ef2c10e64c2   postgres:13             "docker-entrypoint.s…"   About an hour ago   Up About an hour (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   airflow-postgres-1
```

3. 컨테이너 진입
```
docker exec -it 3ef2c10e64c2 /bin/bash
```

4. 유저 설정
```angular2html
psql -U airflow
```

5. `database` 생성
```angular2html
CREATE DATABASE wrtncrack;
```

6. 데이터 베이스 cursor 변경 및 `schema` 생성
```angular2html
\c wrtncrack
CREATE SCHEMA crack;
```

<br>

## ✔ 컨테이너 빌드 (데이터 수집 스크립트)

1. 로컬 레지스트리 이미지 등록
- `docker` 디렉토리로 이동합니다.
- 다음 명령어와 디렉토리에 `Dockerfile`를 이용해 이미지를 빌드합니다.
```bash
docker build -t crack_image .
```

2. 이미지 목록 확인
- 다음 명령어를 통해 방금 등록한 이미지 확인이 가능합니다.
```bash
docker images
```

```angular2html
REPOSITORY      TAG
crack_image     latest
```

<br>

## ✔ Docker demon connection 설정
- `DockerOperator`를 위해 `airflow` 컨테이너와 `docker demon`의 connection을 설정해줍니다.
- `UI` -> `Admin` -> `connection`
- 아래의 3가지 설정후 `SAVE`
```
1. Connection Id   : docker
2. Connection Type : Docker
```
3. `Extra`
```json
{
  "host":"unix://var/run/docker.sock",
  "reauth": false
}
```
<img src="https://github.com/user-attachments/assets/a6c04701-93f7-4ade-bbe3-d2115579de21">

<br>

## ✔ dag run
- `localhost:8080` 진입 
- `crawler_dag`를 `unpause` 이후 `DB`에 데이터가 적재됩니다.


