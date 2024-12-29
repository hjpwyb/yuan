import json
import requests
import re
from time import sleep
from datetime import datetime

# GitHub 配置
GITHUB_TOKEN = "YOUR_ACTUAL_GITHUB_TOKEN"  # 请替换为您的 GitHub Token
OWNER = "hjpwyb"
REPO = "yuan"
FILE_PATH = "tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

# 要匹配的特定字样
VALID_KEYWORDS = "24小时在线匹配首次免费"
BASE_URL = "http://7470ck.cc/vodtype/8-{page}.html"  # 假设分类页面的 URL 格式

# 获取当前日期和时间
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 获取文件内容
def fetch_file():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[{get_current_time()}] Failed to fetch file. Status code: {response.status_code}")
        return None

# 获取文件的 SHA 值
def get_file_sha():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()["sha"]
    else:
        print(f"[{get_current_time()}] Failed to fetch SHA. Status code: {response.status_code}")
        return None

# 更新 JSON 文件中的域名
def update_json_file(json_data, new_domain, sha):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    commit_message = f"Update domain to {new_domain} in JSON file"

    # 更新 JSON 数据中的所有域名字段
    for key in json_data:
        if isinstance(json_data[key], str) and '7470ck.cc' in json_data[key]:
            json_data[key] = json_data[key].replace('7470ck.cc', new_domain)

    # 推送更新
    data = {
        "message": commit_message,
        "content": json.dumps(json_data, ensure_ascii=False),  # 将 JSON 转为字符串
        "sha": sha
    }

    response = requests.put(GITHUB_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        print(f"[{get_current_time()}] Successfully updated the file.")
    else:
        print(f"[{get_current_time()}] Failed to update the file. Status code: {response.status_code}")
        print(f"Response: {response.json()}")

# 尝试访问分类页并判断是否为有效域名
def check_valid_domain(page_number):
    url = BASE_URL.format(page=page_number)
    response = requests.get(url)

    if response.status_code == 200:
        page_content = response.text
        if VALID_KEYWORDS in page_content:
            print(f"[{get_current_time()}] Found valid domain at page {page_number}")
            domain_match = re.search(r"(http://\d{4,5})", page_content)
            if domain_match:
                return domain_match.group(1)  # 返回有效域名
        else:
            print(f"[{get_current_time()}] No valid keyword found on page {page_number}")
    else:
        print(f"[{get_current_time()}] Failed to fetch page {page_number}. Status code: {response.status_code}")
    return None

# 主程序
def main():
    sha = get_file_sha()  # 获取文件的 SHA 值
    if sha:
        json_data = fetch_file()  # 获取文件内容
        if json_data:
            valid_domain = None
            page_number = 2  # 从第二页开始检查
            while valid_domain is None and page_number < 100:  # 假设最多检查 100 页
                valid_domain = check_valid_domain(page_number)
                page_number += 1
                sleep(2)  # 等待 2 秒钟再试下一页

            if valid_domain:
                print(f"[{get_current_time()}] Valid domain found: {valid_domain}")
                update_json_file(json_data, valid_domain, sha)  # 更新 JSON 文件
            else:
                print(f"[{get_current_time()}] No valid domain found.")
        else:
            print(f"[{get_current_time()}] Error fetching JSON file.")
    else:
        print(f"[{get_current_time()}] Failed to fetch SHA.")

# 定时执行更新
def schedule_updates():
    while True:
        main()
        print(f"[{get_current_time()}] Waiting for next update...")
        sleep(3600)  # 每小时更新一次

if __name__ == "__main__":
    schedule_updates()
