import os
import requests
import json
import re
import base64

# GitHub 更新部分
GITHUB_URL = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # 从环境变量中读取 GitHub Token
if not GITHUB_TOKEN:
    print("GitHub Token (GH_TOKEN) is not set.")
    exit(1)  # 如果 Token 没有设置，直接退出
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 拉取原始 JSON 文件
def fetch_json():
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        return None

# 替换 JSON 中域名的数字部分
def update_json(json_data, old_domain, new_domain):
    updated = False
    for key in json_data:
        if isinstance(json_data[key], str) and old_domain in json_data[key]:
            json_data[key] = json_data[key].replace(old_domain, new_domain)
            updated = True  # 标记为已更新
            print(f"Replaced domain in {key}")
    return json_data, updated

# 将更新后的内容推送到 GitHub
def push_to_github(updated_json):
    content = base64.b64encode(json.dumps(updated_json, ensure_ascii=False).encode("utf-8")).decode("utf-8")
    data = {
        "message": "Updated domain in JSON file",
        "content": content,
        "sha": "sha_from_api_response"  # 使用 GitHub API 获取文件的 sha 值
    }
    response = requests.put(GITHUB_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        print("Successfully updated the file on GitHub.")
    else:
        print(f"Failed to push changes to GitHub. Status code: {response.status_code}")

def main():
    # 获取原始 JSON 数据
    json_data = fetch_json()
    if not json_data:
        print("No JSON data found.")
        return

    # 假设你已经找到了新的有效域名
    new_domain = "1234ab.cc"
    old_domain = "7465ck.cc"

    # 更新 JSON 文件内容
    updated_json, updated = update_json(json_data, old_domain, new_domain)

    if updated:
        # 通过 GitHub API 推送更改
        push_to_github(updated_json)
    else:
        print("No changes were made to the JSON file.")

if __name__ == "__main__":
    main()
