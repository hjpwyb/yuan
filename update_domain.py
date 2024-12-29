import requests
from bs4 import BeautifulSoup
import json
import re

# GitHub 更新部分
GITHUB_URL = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"  # 填入你的 GitHub Token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 通过URL抓取网页内容
def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch page {url}. Status code: {response.status_code}")
        return None

# 检查网页内容是否包含有效的域名标志
def check_for_valid_domain(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    # 查找特定的字眼“24小时在线匹配首次免费”
    if "24小时在线匹配首次免费" in soup.get_text():
        print("Valid domain found on the page!")
        return True
    else:
        return False

# 提取网页中的有效域名
def extract_valid_domain(url):
    # 假设有效的域名总是出现在 URL 中
    match = re.search(r'http://(\S+?)(?=\s|/)', url)  # 提取域名部分
    if match:
        return match.group(1)
    return None

# 获取JSON文件并提取域名
def fetch_json():
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        return None

# 替换JSON中所有指定的域名
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

# 将更新后的JSON推送到GitHub
def push_to_github(updated_json):
    # 获取文件当前内容的SHA
    response = requests.get(GITHUB_URL, headers=HEADERS)
    if response.status_code == 200:
        sha = response.json().get("sha")
        if sha:
            data = {
                "message": "Updated domain in JSON file",
                "sha": sha,
                "content": json.dumps(updated_json, ensure_ascii=False).encode("utf-8").decode("utf-8")
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
    base_url = "http://7473ck.cc/vodtype/8-2.html"  # 这是分页的基本URL
    valid_domain = None
    
    # 尝试抓取多个分页并检查有效的域名
    for page_num in range(1, 6):  # 假设最多检查5页
        page_url = base_url.replace("8-2", f"8-{page_num}")
        print(f"Checking page: {page_url}")
        page_content = fetch_page(page_url)
        
        if page_content and check_for_valid_domain(page_content):
            # 提取有效的域名
            valid_domain = extract_valid_domain(page_url)
            if valid_domain:
                print(f"Found valid domain: {valid_domain}")
                break
    
    if valid_domain:
        # 获取现有的JSON文件
        json_data = fetch_json()
        if json_data:
            # 替换JSON中的域名
            old_domain = "7465ck.cc"  # 假设我们要替换的是这个旧域名
            updated_json = replace_domain_in_json(json_data, old_domain, valid_domain)
            
            # 推送更新到GitHub
            push_to_github(updated_json)
        else:
            print("Failed to fetch JSON data.")
    else:
        print("No valid domain found in the pages.")

if __name__ == "__main__":
    main()
