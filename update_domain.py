import requests
import random
import json

# GitHub API 地址（用于获取和更新文件）
repo_url = "https://api.github.com/repos/hjpwyb/yuan/contents/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json"
token = "your_github_personal_access_token"  # 在 GitHub 上生成的个人访问令牌
headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}

# 获取现有的 JSON 文件
response = requests.get(repo_url, headers=headers)

if response.status_code == 200:
    # 获取文件内容和 sha
    file_info = response.json()
    sha = file_info["sha"]
    content = file_info["content"]
    
    # 解码文件内容
    json_data = json.loads(requests.utils.unquote(content))
    
    # 随机选择一个域名
    domain = random.choice(["7473", "7474", "7475", "7476", "7477", "7478", "7479", "7480"])
    
    # 更新 JSON 文件中的域名部分
    json_data["首页推荐链接"] = json_data["首页推荐链接"].replace("{domain}", domain)
    json_data["分类链接"] = json_data["分类链接"].replace("{domain}", domain)
    json_data["搜索链接"] = json_data["搜索链接"].replace("{domain}", domain)
    json_data["搜索片单链接加前缀"] = json_data["搜索片单链接加前缀"].replace("{domain}", domain)
    
    # 生成更新后的 JSON 内容
    updated_content = json.dumps(json_data, indent=4)

    # GitHub API 请求体
    data = {
        "message": "Update domain in config.json",
        "content": updated_content,
        "sha": sha
    }

    # 提交更新
    update_response = requests.put(repo_url, headers=headers, json=data)

    if update_response.status_code == 200:
        print("文件更新成功！")
    else:
        print(f"更新失败: {update_response.status_code}")
else:
    print(f"无法获取文件信息: {response.status_code}")
