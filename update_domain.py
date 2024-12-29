import requests
import re
import json

# 设置文件和目标URL
json_url = "https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 获取JSON文件内容
def fetch_json():
    response = requests.get(json_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch JSON. Status code: {response.status_code}")
        return None

# 检查网页中是否包含有效的域名
def find_valid_domain():
    test_domains = ["7465ck.cc", "7473ck.cc", "example.com"]  # 你可以在这里添加更多的尝试域名
    for domain in test_domains:
        test_url = f"http://{domain}/vodtype/8-2.html"
        try:
            page = requests.get(test_url, headers=headers)
            if page.status_code == 200:
                print(f"Trying domain: {domain}")
                # 如果网页内容包含"24小时在线匹配首次免费"，则返回该域名
                if "24小时在线匹配首次免费" in page.text:
                    print(f"Found valid domain: {domain}")
                    return domain  # 返回有效的域名
        except requests.exceptions.RequestException as e:
            print(f"Error fetching test URL: {test_url} - {e}")
    return None

# 替换JSON中的域名
def replace_domain_in_json(json_data, new_domain):
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
            json_data[key] = json_data[key].replace("7473ck.cc", new_domain)
    
    return json_data

# 推送更新后的JSON到GitHub
def push_to_github(updated_json):
    github_url = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
    token = "YOUR_GITHUB_TOKEN"  # 在这里替换为你的GitHub Token
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }

    # 获取文件当前内容的SHA
    response = requests.get(github_url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha")
        if sha:
            data = {
                "message": "Updated domain in JSON file",
                "sha": sha,
                "content": json.dumps(updated_json, ensure_ascii=False).encode("utf-8").decode("utf-8")
            }
            response = requests.put(github_url, headers=headers, json=data)
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
    # 获取当前有效域名
    new_domain = find_valid_domain()
    if new_domain:
        # 获取现有JSON数据
        json_data = fetch_json()
        if json_data:
            # 更新JSON中的域名
            updated_json = replace_domain_in_json(json_data, new_domain)
            # 推送更新后的文件到GitHub
            push_to_github(updated_json)
        else:
            print("Error fetching JSON data.")
    else:
        print("No valid domain found.")

if __name__ == "__main__":
    main()
