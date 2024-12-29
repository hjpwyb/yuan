import requests
import json
import base64
import os  # 导入 os 模块来获取环境变量

# GitHub 文件 URL
GITHUB_URL = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"

# 从环境变量中获取 GitHub Token
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 通过环境变量获取 'YOU_TOKEN'

# 确保 GITHUB_TOKEN 存在
if not GITHUB_TOKEN:
    raise ValueError("GitHub token (YOU_TOKEN) not found in environment variables.")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 尝试访问指定网址并返回有效性
def check_url(url):
    try:
        response = requests.get(url, timeout=10)  # 设置超时为 10 秒
        if response.status_code == 200:
            print(f"Valid domain found: {url}")
            return url
        else:
            print(f"Invalid domain: {url} (Status code: {response.status_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return None

# 获取 JSON 文件并提取域名
def fetch_json():
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        print(response.text)  # 打印详细错误信息
        return None

# 替换 JSON 中所有含有 ck.cc 的域名
def replace_domain_in_json(json_data, old_domain, new_domain):
    # 递归遍历 JSON 中的所有字段，并替换含有 old_domain 的域名
    if isinstance(json_data, dict):  # 如果是字典，递归处理
        for key, value in json_data.items():
            json_data[key] = replace_domain_in_json(value, old_domain, new_domain)
    elif isinstance(json_data, list):  # 如果是列表，遍历每个元素
        for i in range(len(json_data)):
            json_data[i] = replace_domain_in_json(json_data[i], old_domain, new_domain)
    elif isinstance(json_data, str):  # 如果是字符串，检查是否包含 old_domain
        if old_domain in json_data:
            json_data = json_data.replace(old_domain, new_domain)  # 替换域名
            print(f"Replaced domain in string: {json_data}")
    
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
    # 假设我们要从7474ck.cc开始试错
    base_url = "http://7474ck.cc/vodtype/9-2.html"  # 要测试的基本 URL
    test_url = base_url

    # 进行试错，依次更换URL中的数字部分
    for i in range(7465, 7475):  # 假设你想测试7465ck.cc到7474ck.cc这几个域名
        url_to_test = test_url.replace("7474ck.cc", f"{i}ck.cc")
        
        # 检查URL有效性
        valid_url = check_url(url_to_test)
        if valid_url:
            # 获取现有的 JSON 文件
            json_data = fetch_json()
            if json_data:
                # 替换 JSON 中的域名
                old_domain = "7465ck.cc"  # 假设我们要替换的是这个旧域名
                updated_json = replace_domain_in_json(json_data, old_domain, valid_url)
                
                # 推送更新到 GitHub
                push_to_github(updated_json)
            break
    else:
        print("No valid domain found after trying all the URLs.")

if __name__ == "__main__":
    main()
