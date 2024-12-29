import requests
import json
import base64

# GitHub 更新部分
GITHUB_URL = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_TOKEN = "GH_TOKEN  # 请在这里填写你的 GitHub Token
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
    # 假设我们要从7465ck.cc开始试错
    base_url = "http://7465ck.cc/vodtype/9-2.html"  # 要测试的基本 URL
    test_url = base_url

    # 进行试错，依次更换URL中的数字部分
    for i in range(7465, 7480):  # 假设你想测试7465ck.cc到7470ck.cc这几个域名
        url_to_test = test_url.replace("7465ck.cc", f"{i}ck.cc")
        
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
