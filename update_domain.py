import os
import requests

# 从环境变量中获取 GitHub Token
github_token = os.getenv("MY_GITHUB_TOKEN")
if not github_token:
    raise Exception("GitHub token not found in environment variables.")

# 设置 GitHub API 请求头，使用 Bearer Token 进行身份验证
headers = {
    "Authorization": f"token {github_token}",
    "Accept": "application/vnd.github.v3+json"
}

# GitHub API 请求 URL，替换为您需要的 URL（例如获取文件内容）
github_api_url = "https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"

# 请求 GitHub API 获取文件内容
response = requests.get(github_api_url, headers=headers)

# 检查响应状态码
if response.status_code == 200:
    print("Successfully fetched JSON.")
    # 在这里处理返回的 JSON 数据
    json_data = response.json()
    # 处理文件的 sha 值等信息
    sha = json_data['sha']  # 假设返回的 JSON 包含 sha 字段
    print(f"SHA: {sha}")
else:
    print(f"Failed to fetch file. Status code: {response.status_code}")
    print(response.json())  # 输出错误信息以帮助调试
