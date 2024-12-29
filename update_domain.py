import requests
import json
import base64

# GitHub 文件 URL
GITHUB_URL = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_TOKEN = "YOU_TOKEN"  # 请在这里填写你的 GitHub Token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 提取域名部分
def extract_domain(url):
    return url.split('/')[2]

# 获取 GitHub 上的 JSON 文件内容
def fetch_json():
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        print(response.text)  # 打印详细错误信息
        return None

# 替换 JSON 中的域名
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

# 将更新后的 JSON 推送到 GitHub
def push_to_github(updated_json):
    # 获取文件当前内容的 SHA
    response = requests.get(GITHUB_URL, headers=HEADERS)
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
            response = requests.put(GITHUB_URL, headers=HEADERS, json=data)
            if response.status_code == 200:
                print("Successfully updated the file on GitHub.")
            else:
                print(f"Failed to push changes to GitHub. Status code: {response.status_code}")
                print(response.text)  # 输出详细错误信息
        else:
            print("Failed to get SHA from the response.")
    else:
        print(f"Failed to fetch file from GitHub. Status code: {response.status_code}")
        print(response.text)  # 输出详细错误信息

# 主程序
def main():
    # 提取有效域名
    valid_url = "http://7474ck.cc/vodtype/9-2.html"
    old_domain = extract_domain("http://7465ck.cc")  # 假设要替换的旧域名
    new_domain = extract_domain(valid_url)  # 提取新域名

    print(f"Replacing domain '{old_domain}' with '{new_domain}' in the JSON file.")

    # 获取现有的 JSON 文件
    json_data = fetch_json()
    if json_data:
        # 替换 JSON 中的域名
        updated_json = replace_domain_in_json(json_data, old_domain, new_domain)
        
        # 推送更新到 GitHub
        push_to_github(updated_json)

if __name__ == "__main__":
    main()
