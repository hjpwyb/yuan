import json
import requests
import base64
import re
import urllib.parse
import os

# GitHub 配置
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 从环境变量中获取 Token
REPO_OWNER = 'hjpwyb'
REPO_NAME = 'yuan'
FILE_PATH = 'tv/XYQHiker/黄色仓库.json'
BRANCH_NAME = 'main'
COMMIT_MESSAGE = '更新链接替换'
VALID_LINKS_FILE_PATH = 'JB/valid_links2.txt'

# URL 编码文件路径
encoded_file_path = urllib.parse.quote(FILE_PATH)

# 下载 valid_links.txt 中的所有新链接
def download_valid_links():
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{VALID_LINKS_FILE_PATH}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()  # 按行分割并返回链接列表
    except requests.exceptions.RequestException as e:
        print(f"下载 valid_links.txt 时发生错误: {e}")
        return []

# 下载 GitHub 上的原始文件内容
def download_json_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        return response.json()  # 返回解析的 JSON 数据
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生错误: {e}")
        return None

# 替换链接
def replace_links_in_json(data, old_link_pattern, new_links):
    def replace_in_dict(d):
        for key, value in d.items():
            if isinstance(value, str):  # 如果值是字符串
                matches = re.findall(old_link_pattern, value)
                for old_link in matches:
                    if old_link:  # 确保找到旧链接
                        for new_link in new_links:
                            print(f"正在替换链接：{old_link} -> {new_link}")
                            value = value.replace(old_link, new_link)
                d[key] = value
            elif isinstance(value, dict):  # 如果值是字典，递归替换
                replace_in_dict(value)
            elif isinstance(value, list):  # 如果值是列表，递归替换
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        replace_in_dict(item)
                    elif isinstance(item, str):
                        matches = re.findall(old_link_pattern, item)
                        for old_link in matches:
                            if old_link:  # 确保找到旧链接
                                for new_link in new_links:
                                    print(f"替换列表中的链接：{old_link} -> {new_link}")
                                    item = item.replace(old_link, new_link)
                        value[idx] = item

    replace_in_dict(data)
    return data

# 获取文件的 SHA 值
def get_file_sha(repo_owner, repo_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        file_info = response.json()
        return file_info['sha']
    except requests.exceptions.RequestException as e:
        print(f"无法获取文件 SHA 值: {e}")
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

    try:
        response = requests.put(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        print("文件已成功更新！")
    except requests.exceptions.RequestException as e:
        print(f"更新文件时发生错误: {e}")

def main():
    json_url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}'
    
    # 定义匹配旧链接的正则表达式 (例如匹配 http://<数字>ck.cc 格式)
    old_link_pattern = r'https?://\d+ck\.cc(?:/.*)?'  # 匹配 http:// 或 https:// 和 以数字开头的链接，并允许路径部分
    
    # 下载 valid_links.txt 中的所有新链接
    new_links = download_valid_links()
    if not new_links:
        print("没有有效链接可用.")
        return

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 打印原始 JSON 数据（调试用）
    print("原始 JSON 数据：")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # 替换链接
    updated_data = replace_links_in_json(data, old_link_pattern, new_links)

    # 打印更新后的 JSON 数据（调试用）
    print("替换后的 JSON 数据：")
    print(json.dumps(updated_data, ensure_ascii=False, indent=2))

    # 获取文件的 SHA 值
    sha = get_file_sha(REPO_OWNER, REPO_NAME, encoded_file_path, BRANCH_NAME)
    if sha is None:
        return

    # 更新 JSON 文件
    update_github_file(REPO_OWNER, REPO_NAME, encoded_file_path, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

if __name__ == "__main__":
    main()
