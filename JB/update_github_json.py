import json
import requests
import os
import base64
import re

# 从环境变量获取 GitHub Token
GITHUB_TOKEN = os.getenv('YOU_TOKEN')
REPO_OWNER = 'hjpwyb'  # 仓库拥有者
REPO_NAME = 'yuan'  # 仓库名称
FILE_PATH = 'tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json'  # 文件路径
BRANCH_NAME = 'main'  # 分支名称
COMMIT_MESSAGE = '更新链接替换'  # 提交信息
VALID_LINKS_FILE_PATH = 'valid_links2.txt'  # 更新后的文件路径，相对于 JB 文件夹

# 下载 GitHub 上的原始文件内容
def download_json_file(url):
    try:
        headers = {"Cache-Control": "no-cache"}  # 禁用缓存
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生错误: {e}")
        return None

# 下载 valid_links.txt 中的所有新链接
def download_valid_links():
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/JB/{VALID_LINKS_FILE_PATH}'
    try:
        headers = {"Cache-Control": "no-cache"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"下载 valid_links.txt 时发生错误: {e}")
        return []

# 替换链接
def replace_links_in_json(data, old_link_pattern, new_links):
    new_links_iter = iter(new_links)  # 创建新链接的迭代器

    def replace_in_dict(d):
        for key, value in d.items():
            if isinstance(value, str):
                value = re.sub(old_link_pattern, lambda _: next(new_links_iter, _), value)
                d[key] = value
            elif isinstance(value, dict):
                replace_in_dict(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        replace_in_dict(value[i])
                    elif isinstance(value[i], str):
                        value[i] = re.sub(old_link_pattern, lambda _: next(new_links_iter, _), value[i])

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

    formatted_content = json.dumps(new_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(formatted_content.encode('utf-8')).decode('utf-8')

    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"文件已成功更新！")
    else:
        print(f"更新文件时发生错误: {response.status_code} - {response.text}")

# 主程序
def main():
    json_url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}'
    old_link_pattern = r'http://\d+hsck\.cc'

    # 下载 valid_links.txt 中的所有新链接
    new_links = download_valid_links()
    print(f"从 GitHub 下载的新链接列表: {new_links}")
    if not new_links:
        print("没有有效链接可用.")
        return

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, old_link_pattern, new_links)
    print("替换后的 JSON 数据：")
    print(json.dumps(updated_data, indent=2, ensure_ascii=False))

    # 获取文件的 SHA 值
    sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)
    if sha is None:
        return

    # 更新 JSON 文件
    update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

# 运行主程序
if __name__ == "__main__":
    main()
