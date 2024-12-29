import os
import requests
import json
import base64
import re

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

# 获取JSON文件并提取域名
def fetch_json():
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        return None

# 查找并替换JSON中的数字域名部分
def replace_numeric_domain_in_json(json_data, old_domain, new_domain):
    """
    替换 JSON 中含有数字部分的域名（数字+域名）
    """
    keys_to_replace = [
        "首页推荐链接",
        "首页片单链接加前缀",
        "分类链接",
        "分类片单链接加前缀",
        "搜索链接",
        "搜索片单链接加前缀",
        "直接播放直链视频请求头"
    ]
    
    # 使用正则表达式查找域名并替换
    domain_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|\d+(\.\d+)+)")

    for key in keys_to_replace:
        if key in json_data:
            original_content = json_data[key]
            # 查找并替换域名
            if isinstance(original_content, str):
                updated_content = domain_pattern.sub(lambda match: new_domain if match.group(0) == old_domain else match.group(0), original_content)
                json_data[key] = updated_content
                print(f"Replaced domain in key '{key}'")
    
    return json_data

# 将更新后的JSON推送到GitHub
def push_to_github(updated_json):
    # 获取文件当前内容的SHA
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        sha = response.json().get("sha")
        if sha:
            # 将更新后的内容格式化为JSON并转换为字符串
            json_content = json.dumps(updated_json, ensure_ascii=False, indent=4)
            
            # Base64 编码更新后的内容
            content = base64.b64encode(json_content.encode("utf-8")).decode("utf-8")
            
            data = {
                "message": "Updated numeric domain in JSON file",
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
    old_domain = "7465ck.cc"  # 假设我们要替换的是这个旧域名
    new_domain = "1234ab.cc"  # 你要替换的新域名
    
    # 获取现有的JSON文件
    json_data = fetch_json()
    if json_data:
        # 替换JSON中的域名
        updated_json = replace_numeric_domain_in_json(json_data, old_domain, new_domain)
        
        # 推送更新到GitHub
        push_to_github(updated_json)
    else:
        print("Failed to fetch JSON data.")

if __name__ == "__main__":
    main()
