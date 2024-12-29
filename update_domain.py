import json
import re
import requests
from time import sleep
from datetime import datetime

# GitHub 配置
GITHUB_TOKEN = "MY_GITHUB_TOKEN"  # 用你的 GitHub token 替换
OWNER = "hjpwyb"
REPO = "yuan"
FILE_PATH = "tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{FILE_PATH}"

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
        print(f"Response: {response.json()}")
        return None

# 更新域名数字
def update_domain_number(json_data):
    # 定义正则表达式来匹配域名部分
    pattern = r"(http://)(\d{4})(\d*)(\.cc)"  # 匹配域名中的数字部分
    url = json_data.get("首页推荐链接")
    
    # 查找并更新数字
    if url:
        match = re.search(pattern, url)
        if match:
            old_number = int(match.group(2))  # 获取当前数字部分
            new_number = old_number + 1  # 增加1
            new_url = url.replace(match.group(2), str(new_number))  # 更新 URL
            json_data["首页推荐链接"] = new_url  # 更新 JSON 数据
            print(f"[{get_current_time()}] Updated domain from {old_number} to {new_number}")
        else:
            print(f"[{get_current_time()}] No valid domain number found in {url}")
    else:
        print(f"[{get_current_time()}] '首页推荐链接' not found in the JSON data")
    
    return json_data

# 推送更新后的文件
def update_file(json_data, sha):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    commit_message = f"Update domain in JSON file at {get_current_time()}"
    
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

# 获取文件的 SHA 值
def get_file_sha():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(GITHUB_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()["sha"]
    else:
        print(f"[{get_current_time()}] Failed to fetch SHA. Status code: {response.status_code}")
        return None

# 主程序
def main():
    sha = get_file_sha()  # 获取文件的 SHA 值
    if sha:
        json_data = fetch_file()  # 获取文件内容
        if json_data:
            updated_json_data = update_domain_number(json_data)  # 更新域名
            update_file(updated_json_data, sha)  # 推送更新
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
