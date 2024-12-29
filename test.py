import json
import requests
import base64
import os
import argparse

# 获取 GitHub Token 从环境变量
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 从环境变量获取 YOU_TOKEN
REPO_OWNER = 'hjpwyb'  # 仓库拥有者
REPO_NAME = 'yuan'  # 仓库名称
FILE_PATH = 'tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json'  # 文件的路径
BRANCH_NAME = 'main'  # 分支名称
COMMIT_MESSAGE = '更新链接替换'  # 提交信息

# 设置命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='替换 JSON 文件中的链接')
    parser.add_argument('--old-link', required=True, help='旧链接')
    parser.add_argument('--new-link', required=True, help='新链接')
    return parser.parse_args()

# 下载 GitHub 上的原始文件内容
def download_json_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生错误: {e}")
        return None

# 替换函数
def replace_links_in_json(data, old_link, new_link):
    def replace_in_dict(d):
        for key, value in d.items():
            if isinstance(value, str):
                if old_link in value:
                    d[key] = value.replace(old_link, new_link)
            elif isinstance(value, dict):
                replace_in_dict(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        replace_in_dict(item)
                    elif isinstance(item, str):
                        if old_link in item:
                            item = item.replace(old_link, new_link)

    replace_in_dict(data)
    return data

# 获取文件的 SHA 值
def get_file_sha(repo_owner, repo_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        return file_info['sha']
    else:
        print(f"无法获取文件 SHA 值: {response.status_code}")
        return None

# 更新 GitHub 上的文件内容
def update_github_file(repo_owner, repo_name, file_path, new_data, sha, branch, commit_message):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    encoded_content = base64.b64encode(json.dumps(new_data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print("文件已成功更新！")
    else:
        print(f"更新文件时发生错误: {response.status_code} - {response.text}")

# 主程序
def main():
    args = parse_arguments()  # 获取命令行参数
    json_url = 'https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json'

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, args.old_link, args.new_link)

    # 获取文件的 SHA 值
    sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)
    if sha is None:
        return

    # 更新文件
    update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
