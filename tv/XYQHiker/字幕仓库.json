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

# 从JSON数据中提取所有的域名
def extract_domains(json_data):
    domains = set()
    # 遍历JSON中的所有值，使用正则表达式提取域名
    domain_pattern = re.compile(r"https?://([a-zA-Z0-9.-]+)")
    
    # 遍历 JSON 中的每个键值对，提取出所有的域名
    for value in json_data.values():
        if isinstance(value, str):
            found_domains = domain_pattern.findall(value)
            for domain in found_domains:
                domains.add(domain)
    
    return list(domains)

# 自动检测当前域名并选择替换
def get_current_and_new_domain(json_data):
    # 提取 JSON 中的所有域名
    domains = extract_domains(json_data)
    
    if len(domains) < 2:
        print("Insufficient domains found for replacement.")
        return None, None
    
    # 假设 JSON 中有两个不同的域名，选择第一个作为当前域名
    current_domain = domains[0]
    
    # 从所有找到的域名中移除当前域名，选择第二个作为新的域名
    new_domain = domains[1] if len(domains) > 1 else None
    
    if new_domain:
        print(f"Found current domain: {current_domain}, preparing to replace with: {new_domain}")
        return current_domain, new_domain
    else:
        print("No valid domain pair found for replacement.")
        return None, None

# 替换JSON中的域名
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
    
    # 循环检查需要替换的键，并将指定的域名替换为新域名
    for key in keys_to_replace:
        if key in json_data:
            json_data[key] = json_data[key].replace(old_domain, new_domain)
    
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
    # 先获取现有的 JSON 数据
    json_data = fetch_json()
    if json_data:
        # 自动检测当前域名并选择替换
        old_domain, new_domain = get_current_and_new_domain(json_data)
        if old_domain and new_domain:
            print(f"Replacing domain {old_domain} with {new_domain}.")
            updated_json = replace_domain_in_json(json_data, old_domain, new_domain)
            # 推送更新后的文件到GitHub
            push_to_github(updated_json)
        else:
            print("No valid domains to replace.")
    else:
        print("Error fetching JSON data.")

if __name__ == "__main__":
    main()
