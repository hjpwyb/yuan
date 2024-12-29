import json
import requests

# 配置您的 GitHub 仓库和文件路径
github_raw_url = "https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/字幕仓库.json"
github_api_url = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/字幕仓库.json"
github_token = "your_github_token"  # 替换为您的 GitHub Token

# 获取 JSON 文件
response = requests.get(github_raw_url)
if response.status_code == 200:
    json_data = response.json()
    print("Successfully fetched JSON.")

    # 在这里修改域名数组
    updated_domains = ["example.com" for domain in json_data["域名"]]

    # 更新 JSON 数据中的域名部分
    json_data["域名"] = updated_domains

    # 提交到 GitHub
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json",
    }

    # 获取文件的 SHA
    api_response = requests.get(github_api_url, headers=headers)
    print("API response:", api_response.json())  # 打印响应内容查看返回的数据结构

    try:
        sha = api_response.json()["sha"]
    except KeyError:
        print("Failed to get SHA from response.")
        print("Response:", api_response.json())
        exit(1)

    # 通过 GitHub API 提交修改
    update_data = {
        "message": "Update domain names in JSON",
        "committer": {
            "name": "GitHub Actions",
            "email": "actions@github.com",
        },
        "sha": sha,
        "content": json.dumps(json_data, ensure_ascii=False),
    }

    update_url = f"{github_api_url}?ref=main"
    update_response = requests.put(update_url, json=update_data, headers=headers)

    if update_response.status_code == 200:
        print("Domain updated successfully!")
    else:
        print(f"Failed to update domain: {update_response.status_code}")
else:
    print(f"Failed to fetch JSON from GitHub: {response.status_code}")
