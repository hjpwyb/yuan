import json
import requests
import base64
import re
import urllib.parse
import os
from typing import List, Dict

# 配置区
GITHUB_TOKEN = os.getenv('YOU_TOKEN')
REPO_OWNER = 'hjpwyb'
REPO_NAME = 'yuan'
FILE_PATH = 'tv/XYQHiker/字幕仓库.json'
BRANCH_NAME = 'main'
COMMIT_MESSAGE = '更新链接替换'
VALID_LINKS_FILE_PATH = 'JB/valid_links.txt'

# 获取文件路径的 URL 编码
encoded_file_path = urllib.parse.quote(FILE_PATH)


def download_file_from_github(url: str) -> List[str]:
    """
    从 GitHub 下载文件内容并按行返回。
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        print(f"下载文件时出错: {e}")
        return []


def fetch_json_from_github(url: str) -> Dict:
    """
    从 GitHub 获取 JSON 文件并返回其内容。
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"获取 JSON 文件时出错: {e}")
        return {}


def replace_links_in_json(data: Dict, pattern: str, replacements: List[str]) -> Dict:
    """
    根据匹配规则替换 JSON 数据中的链接。
    """
    replacement_iter = iter(replacements)  # 使用迭代器防止重复使用

    def replace_match(match: re.Match) -> str:
        try:
            return next(replacement_iter)
        except StopIteration:
            return match.group(0)

    def recursive_replace(item):
        if isinstance(item, str):
            return re.sub(pattern, replace_match, item)
        elif isinstance(item, list):
            return [recursive_replace(i) for i in item]
        elif isinstance(item, dict):
            return {k: recursive_replace(v) for k, v in item.items()}
        return item

    return recursive_replace(data)


def upload_to_github(repo_owner: str, repo_name: str, file_path: str, data: Dict, sha: str, branch: str, message: str):
    """
    将修改后的文件上传到 GitHub。
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=2).encode()).decode()
    
    payload = {
        "message": message,
        "content": content,
        "sha": sha,
        "branch": branch,
    }

    try:
        response = requests.put(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        print("文件已成功上传到 GitHub！")
    except requests.RequestException as e:
        print(f"上传文件时出错: {e}")


def get_sha(repo_owner: str, repo_name: str, file_path: str, branch: str) -> str:
    """
    获取文件的 SHA 值。
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("sha")
    except requests.RequestException as e:
        print(f"获取 SHA 值时出错: {e}")
        return ""


def main():
    json_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}"
    links_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{VALID_LINKS_FILE_PATH}"

    # 匹配规则
    old_link_pattern = r"http://\d+ck\.cc"

    # 下载新链接和 JSON 文件
    new_links = download_file_from_github(links_url)
    if not new_links:
        print("未找到有效链接，终止操作。")
        return

    data = fetch_json_from_github(json_url)
    if not data:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, old_link_pattern, new_links)

    # 获取 SHA 值并上传
    sha = get_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)
    if not sha:
        return

    upload_to_github(REPO_OWNER, REPO_NAME, FILE_PATH, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)


if __name__ == "__main__":
    main()
