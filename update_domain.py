import requests
import json
import os

# 获取 GitHub 上的 JSON 文件
repo_url = "https://raw.githubusercontent.com/username/repository/main/tv/XYQHiker/字幕仓库.json"  # 请根据实际路径修改
headers = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",  # 使用 GitHub Actions 提供的 Token
}

# 获取 JSON 文件内容
response = requests.get(repo_url, headers=headers)

if response.status_code == 200:
    json_data = response.json()
else:
    raise Exception(f"Failed to fetch JSON from GitHub: {response.status_code}")

# 更新 JSON 数据（示例：更改 domain 部分）
# 假设您要替换 JSON 中的某个字段（例如 '首页推荐链接'）
for domain in ['7473', '7474', '7475', '7476']:
    json_data['首页推荐链接'] = f"http://{domain}ck.cc"

# 保存更新后的 JSON 文件
json_file_path = 'tv/XYQHiker/字幕仓库.json'  # 请确保路径正确

# 将更新后的 JSON 内容写入文件
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

print("Domain updated successfully!")
