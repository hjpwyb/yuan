import os
import requests
import json
import base64

# GitHub URL（直接访问 raw 内容）
GITHUB_URL = "https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_API_URL = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_TOKEN = os.getenv("GH_TOKEN")  # 从环境变量中读取 GitHub Token
if not GITHUB_TOKEN:
    print("GitHub Token (GH_TOKEN) is not set.")
    exit(1)  # 如果 Token 没有设置，直接退出

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 读取文件内容
def fetch_json():
    response = requests.get(GITHUB_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        return None

# 替换 JSON 中指定的域名
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
    
    for key in keys_to_replace:
        if key in json_data:
            json_data[key] = json_data[key].replace(old_domain, new_domain)
            print(f"Replaced domain in key '{key}'")
    return json_data

# 更新文件到 GitHub
def push_to_github(updated_json):
    # 获取文件当前内容的 SHA
    response = requests.get(GITHUB_API_URL, headers=HEADERS)
    if response.status_code == 200:
        sha = response.json().get("sha")
        if sha:
            # Base64 编码更新后的内容
            content = base64.b64encode(json.dumps(updated_json, ensure_ascii=False).encode("utf-8")).decode("utf-8")
            
            data = {
                "message": "Updated domain in JSON file",
                "sha": sha,
                "content": content
            }
            response = requests.put(GITHUB_API_URL, headers=HEADERS, json=data)
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
    old_domain = "7465ck.cc"  # 假设要替换的旧域名
    new_domain = "1234ab.cc"  # 这是你希望替换的新域名

    # 获取 JSON 数据
    json_data = fetch_json()
    if json_data:
        # 替换域名
        updated_json = replace_domain_in_json(json_data, old_domain, new_domain)
        
        # 如果有更改，则推送到 GitHub
        if updated_json != json_data:
            push_to_github(updated_json)
        else:
            print("No changes were made to the JSON file.")
    else:
        print("Failed to fetch JSON data.")

if __name__ == "__main__":
    main()
