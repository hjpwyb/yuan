import json
import requests
import base64
import os

# GitHub API 配置
GITHUB_URL = "https://api.github.com/repos/yourusername/yourrepo/contents/yourjsonfile.json"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # 从环境变量中读取 GitHub Token
if not GITHUB_TOKEN:
    print("GitHub Token (GH_TOKEN) is not set.")
    exit(1)  # 如果 Token 没有设置，直接退出
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 通过 API 获取 JSON 文件
def fetch_json():
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        return None

# 替换 JSON 中的域名（只替换包含数字部分的域名）
def replace_domain_in_json(json_data, old_domain, new_domain):
    keys_to_replace = [
        "首页推荐链接",
        "首页片单链接加前缀",
        "分类链接",
        "分类片单链接加前缀",
        "搜索链接",
        "搜索片单链接加前缀",
        "直接播放直链视频请求头"
    ]
    
    updated = False  # 标记是否有更新

    for key in keys_to_replace:
        if key in json_data:
            if old_domain in json_data[key]:  # 检查是否包含旧域名
                json_data[key] = json_data[key].replace(old_domain, new_domain)
                updated = True  # 标记为更新
                print(f"Replaced domain in key '{key}'")

    return json_data, updated

# 将更新后的 JSON 文件推送到 GitHub
def push_to_github(updated_json):
    # 获取文件当前内容的 SHA
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        sha = response.json().get("sha")
        if sha:
            # Base64 编码更新后的内容
            content = base64.b64encode(json.dumps(updated_json, ensure_ascii=False).encode("utf-8")).decode("utf-8")
            
            data = {
                "message": "Update domain in JSON",
                "sha": sha,
                "content": content
            }
            response = requests.put(GITHUB_URL, headers=HEADERS, json=data)
            if response.status_code == 200:
                print("Successfully updated the file on GitHub.")
            else:
                print(f"Failed to push changes to GitHub. Status code: {response.status_code}")
        else:
            print("Failed to get SHA from the response.")
    else:
        print(f"Failed to fetch file from GitHub. Status code: {response.status_code}")

# 主程序
def main():
    old_domain = "7465ck.cc"  # 要替换的旧域名
    new_domain = "1234ab.cc"  # 新域名
    
    # 获取现有的 JSON 文件
    json_data = fetch_json()
    if json_data:
        # 替换 JSON 中的域名
        updated_json_data, updated = replace_domain_in_json(json_data, old_domain, new_domain)
        
        if updated:
            # 推送更新到 GitHub
            push_to_github(updated_json_data)
        else:
            print("No changes were made to the JSON file.")
    else:
        print("Failed to fetch JSON data.")

if __name__ == "__main__":
    main()
