import requests
import json
import os

# GitHub 仓库文件 URL
repo_url = "https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/字幕仓库.json"  # 确保路径正确
print(f"Trying to fetch JSON from: {repo_url}")

# 获取文件内容
response = requests.get(repo_url)

if response.status_code == 200:
    json_data = response.json()
    print("Successfully fetched JSON.")
else:
    print(f"Failed to fetch JSON. HTTP Status Code: {response.status_code}")
    print("Response text:", response.text)  # 输出响应的详细信息，帮助调试

# 更新 JSON 数据（示例：更改域名部分）
for domain in ['7473', '7474', '7475', '7476']:
    json_data['首页推荐链接'] = f"http://{domain}ck.cc"

# 保存更新后的 JSON 文件
json_file_path = 'tv/XYQHiker/字幕仓库.json'

with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

print("Domain updated successfully!")
