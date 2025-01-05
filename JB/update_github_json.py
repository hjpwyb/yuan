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
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"下载 JSON 文件时发生错误: {e}")
        return None

# 下载 valid_links.txt 中的所有新链接
def download_valid_links():
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/JB/{VALID_LINKS_FILE_PATH}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.exceptions.RequestException as e:
        print(f"下载 valid_links.txt 时发生错误: {e}")
        return []

# 替换链接
def replace_links_in_json(data, old_link_pattern, new_links):
    new_links_iter = iter(new_links)
    replaced_count = 0

    def replace_in_dict(d):
        nonlocal replaced_count
        for key, value in d.items():
            if isinstance(value, str):
                # 替换匹配的旧链接
                new_value, n_replacements = re.subn(old_link_pattern, lambda _: next(new_links_iter, _.group(0)), value)
                if n_replacements > 0:
                    print(f"替换链接：{value} -> {new_value}")
                    replaced_count += n_replacements
                d[key] = new_value
            elif isinstance(value, dict):
                replace_in_dict(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        replace_in_dict(value[i])
                    elif isinstance(value[i], str):
                        new_value, n_replacements = re.subn(old_link_pattern, lambda _: next(new_links_iter, _.group(0)), value[i])
                        if n_replacements > 0:
                            print(f"替换链接：{value[i]} -> {new_value}")
                            replaced_count += n_replacements
                        value[i] = new_value

    replace_in_dict(data)
    print(f"总共替换了 {replaced_count} 个链接")
    return data

# 获取文件的 SHA 值
def get_file_sha(repo_owner, repo_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('sha')
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
        print("文件已成功更新！")
    else:
        print(f"更新文件时发生错误: {response.status_code} - {response.text}")

# 主程序
def main():
    json_url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}'
    old_link_pattern = r'http://\d+ck\.cc'  # 匹配链接

    new_links = download_valid_links()
    if not new_links:
        print("没有可用的新链接，退出程序。")
        return

    print(f"下载的新链接列表：{new_links}")

    data = download_json_file(json_url)
    if data is None:
        return

    updated_data = replace_links_in_json(data, old_link_pattern, new_links)
    print("替换后的 JSON 数据：", json.dumps(updated_data, indent=2, ensure_ascii=False))

    sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)
    if sha is None:
        return

    update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

# 运行主程序
if __name__ == "__main__":
    main()
