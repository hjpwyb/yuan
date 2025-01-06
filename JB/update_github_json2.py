import json
import requests
import re
import base64
import urllib.parse
import os

# GitHub 配置
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 从环境变量中获取 Token
REPO_OWNER = 'hjpwyb'
REPO_NAME = 'yuan'
FILE_PATH = 'tv/XYQHiker/黄色仓库.json'
BRANCH_NAME = 'main'
COMMIT_MESSAGE = '批量替换链接'
VALID_LINKS_FILE_PATH = 'JB/valid_links2.txt'

# URL 编码文件路径
encoded_file_path = urllib.parse.quote(FILE_PATH)

# 下载 valid_links2.txt 的所有新链接
def download_valid_links():
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{VALID_LINKS_FILE_PATH}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()  # 按行分割链接
    except requests.exceptions.RequestException as e:
        print(f"下载 valid_links2.txt 时发生错误: {e}")
        return []

# 下载 GitHub 上的 JSON 文件内容
def download_json_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # 返回解析后的 JSON 数据
    except requests.exceptions.RequestException as e:
        print(f"下载 JSON 文件时发生错误: {e}")
        return None

# 替换 JSON 数据中的链接
def replace_links_in_json(data, old_link_pattern, new_links):
    new_links_iter = iter(new_links)  # 创建迭代器

    def replace_recursive(item):
        if isinstance(item, str):
            matches = re.findall(old_link_pattern, item)
            for old_link in matches:
                try:
                    new_link = next(new_links_iter)
                    print(f"替换链接：{old_link} -> {new_link}")
                    item = item.replace(old_link, new_link)
                except StopIteration:
                    print("新链接用完，停止替换。")
                    break
            return item
        elif isinstance(item, dict):
            return {key: replace_recursive(value) for key, value in item.items()}
        elif isinstance(item, list):
            return [replace_recursive(elem) for elem in item]
        return item

    return replace_recursive(data)

# 获取文件的 SHA 值
def get_file_sha(repo_owner, repo_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['sha']
    except requests.exceptions.RequestException as e:
        print(f"获取文件 SHA 值失败: {e}")
        return None

# 更新 GitHub 上的 JSON 文件
def update_github_file(repo_owner, repo_name, file_path, updated_data, sha, branch, commit_message):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # 将 JSON 数据转为字符串并编码为 Base64
    json_content = json.dumps(updated_data, ensure_ascii=False, indent=2)
    encoded_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')

    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,
        "branch": branch
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print("文件更新成功！")
    except requests.exceptions.RequestException as e:
        print(f"更新文件时发生错误: {e}")

def main():
    json_url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}'
    
    # 匹配旧链接的正则表达式 (以 http:// 或 https:// 开头，包含数字的域名)
    old_link_pattern = r'https?://\d+ck\.cc(?:/.*)?'
    
    # 下载新链接
    new_links = download_valid_links()
    if not new_links:
        print("没有可用的新链接。")
        return

    # 下载 JSON 数据
    data = download_json_file(json_url)
    if data is None:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, old_link_pattern, new_links)

    # 获取文件 SHA
    sha = get_file_sha(REPO_OWNER, REPO_NAME, encoded_file_path, BRANCH_NAME)
    if sha is None:
        return

    # 更新文件
    update_github_file(REPO_OWNER, REPO_NAME, encoded_file_path, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
