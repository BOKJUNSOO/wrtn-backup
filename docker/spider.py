import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import pandas as pd
from datetime import datetime
import requests
from sqlalchemy import create_engine
import json
import numpy as np

# meta data
dict_ = {
    "navigation_container": "div.css-h1fkhq.e112o4s61",
    "navigation_element": "p.css-13ahzj4.e112o4s61"
}

# database connenction
conn_params = {
    "host": "postgres",
    "port": 5432,
    "dbname": "wrtncrack",
    "user": "airflow",
    "password": "airflow"
}
db_info = {
    "schema": "crack"
}

#
start_url = "https://crack.wrtn.ai/?pageId=682c89c39d1325983179b65b"
not_category = ["추천", "랭킹", "오늘 신작", "남성 인기", "여성 인기"]
created_at = datetime.now().strftime("%Y-%m-%d")

#
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# first rendering
driver = webdriver.Chrome(options=chrome_options)
driver.get(start_url)

# get navigation bar element
navigation_container = driver.find_element(By.CSS_SELECTOR, dict_["navigation_container"])
navigation_elements = navigation_container.find_elements(By.CSS_SELECTOR, dict_["navigation_element"])
nav_list = []

for idx, nav in enumerate(navigation_elements):
    if nav.text in not_category:
        continue
    nav_list.append({
        "name": nav.text
    })

category_df = pd.DataFrame(nav_list)

category_df.insert(0, "id", range(1, len(category_df) + 1))
category_list = list(category_df["name"])

# get base urls
seen_urls = set()
for idx, category_text in enumerate(category_list):
    try:
        category_container = driver.find_element(By.CSS_SELECTOR, dict_["navigation_container"])
        all_categories = category_container.find_elements(By.CSS_SELECTOR, dict_["navigation_element"])

        matching = [c for c in all_categories if c.text.strip() == category_text.strip()]
        category_element = matching[0]

        print(category_element.text)

        previous_len = len(driver.requests)
        driver.execute_script("arguments[0].click();", category_element)

        time.sleep(2)

        new_request = None
        for request in driver.requests[previous_len:]:
            if (
                    request.response and
                    "contents-api.wrtn.ai/character/characters" in request.url and
                    request.url not in seen_urls
            ):
                seen_urls.add(request.url)
                new_request = request
                break

        if new_request:
            print(f"[INFO] - {category_text} base URL: {new_request.url}")

    except Exception as e:
        print(f"[ERROR] - {category_text}: {e}")

# request api with base URL
seen_urls = list(seen_urls)

headers = {
    "User-Agent": "Mozilla/5.0"
}

# initial params
params = {
    "limit": 12
}

crawling_data_list = []
for idx, base_url in enumerate(seen_urls):
    print(f"[INFO] - Now request url:{idx + 1}/", len(seen_urls))
    cursor = None
    while True:
        if cursor:
            params["cursor"] = cursor
        else:
            params.pop("cursor", None)

        for retry in range(4):
            response = requests.get(base_url, headers=headers, params=params)
            if response.status_code == 200:
                break
            else:
                print("[ERROR] - server Error")
                time.sleep(10)
                print(f"[INFO] - retry after 10 seconds : {retry + 1}/4")

        data = response.json()
        data = data["data"]

        for character in data["characters"]:
            print(base_url, ":", character.get("name"))
            profile_image = character.get("profileImage") or {}
            origin_url = profile_image.get("origin") if profile_image else None

            crawl_data = {
                "character_name": character.get("name"),
                "character_info": character.get("description"),
                "character_image": origin_url,
                "character_message": character.get("initialMessages"),
                "category_name": character["promptTemplate"]["name"],
                "created_at": created_at
            }
            crawling_data_list.append(crawl_data)

        cursor = data["nextCursor"]

        # cursor 가 더이상 없다면
        if cursor is None:
            print(f"[INFO] - {base_url}의 데이터를 모두 수집했습니다.")
            break

        time.sleep(0.4)

crawl_df = pd.DataFrame(crawling_data_list)
crawl_df.insert(0, "id", range(1, len(crawl_df) + 1))

stack = set(crawl_df["category_name"])
stack = list(stack)

category_data = []
for idx, category in enumerate(stack):
    data = {
        "id": idx + 1,
        "category_name": category
    }
    category_data.append(data)

category_df = pd.DataFrame(category_data)
print(category_df)

crawl_df = crawl_df.merge(
    category_df[['id', 'category_name']],
    on='category_name',
    how='left'
)

crawl_df = crawl_df.rename(columns={'id_x': 'id',
                                    'id_y': 'category_id'})


# list type 데이터 처리
def list_to_json(val):
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    return val


crawl_df['character_message'] = crawl_df['character_message'].map(list_to_json)


# NUL 데이터 처리
def full_clean(val):
    try:
        if isinstance(val, bytes):
            val = val.replace(b'\x00', b'').decode('utf-8', errors='ignore')
        if isinstance(val, (list, dict)):
            return json.dumps(val, ensure_ascii=False)
        if isinstance(val, str):
            return val.replace('\x00', '')
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return ''
        return str(val)
    except:
        return ''


crawl_df = crawl_df.applymap(full_clean).astype(str)

# 저장
engine = create_engine(
    f'postgresql+psycopg2://{conn_params["user"]}:{conn_params["password"]}@{conn_params["host"]}:{conn_params["port"]}/{conn_params["dbname"]}'
)

# 크롤링 데이터 저장
try:
    with engine.begin() as conn:  # 트랜잭션 자동 처리
        crawl_df.to_sql(
            name='character_info',
            con=conn,
            schema=db_info["schema"],
            if_exists='replace',  # append, replace, fail 중 선택
            index=False,
        )
        print("[INFO] - 데이터가 성공적으로 저장되었습니다.")
except Exception as e:
    print(f"[ERROR] 저장 중 에러 발생: {e}")

# 카테고리 리스트 저장
try:
    with engine.begin() as conn:  # 트랜잭션 자동 처리
        category_df.to_sql(
            name='character_category',
            con=conn,
            schema=db_info["schema"],
            if_exists='replace',  # append, replace, fail 중 선택
            index=False,
        )
        print("[INFO] - 데이터가 성공적으로 저장되었습니다.")
except Exception as e:
    print(f"[ERROR] 저장 중 에러 발생: {e}")