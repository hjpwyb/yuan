import json
import requests
import os
import base64
import re  # 导入正则表达式模块

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
        response.raise_for_status()  # 确保请求成功
        return response.json()  # 返回解析的 JSON 数据
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生错误: {e}")
        return None

# 下载 valid_links.txt 中的所有新链接
def download_valid_links():
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/JB/{VALID_LINKS_FILE_PATH}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()  # 按行分割并返回链接列表
    except requests.exceptions.RequestException as e:
        print(f"下载 valid_links.txt 时发生错误: {e}")
        return []

# 替换链接
def replace_links_in_json(data, old_link_pattern, new_links):
    new_links_iter = iter(new_links)  # 创建新链接的迭代器

    def replace_in_dict(d):
        for key, value in d.items():
            if isinstance(value, str):
                # 使用正则表达式查找并替换匹配的旧链接
                d[key] = re.sub(old_link_pattern, lambda _: next(new_links_iter, _.group(0)), value)
            elif isinstance(value, dict):  # 如果值是字典，递归替换
                replace_in_dict(value)
            elif isinstance(value, list):  # 如果值是列表，递归替换
                for i in range(len(value)):
                    if isinstance(value[i], dict):
                        replace_in_dict(value[i])
                    elif isinstance(value[i], str):
                        value[i] = re.sub(old_link_pattern, lambda _: next(new_links_iter, _.group(0)), value[i])

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

    # 重新格式化 JSON 数据为字符串，并且保留原始的格式
    formatted_content = json.dumps(new_data, ensure_ascii=False, indent=2)

    # 将新数据转换为 base64 编码
    encoded_content = base64.b64encode(formatted_content.encode('utf-8')).decode('utf-8')

    # 构建请求体
    data = {
        "message": commit_message,
        "content": encoded_content,
        "sha": sha,  # 文件的 SHA 值
        "branch": branch
    }

    # 发送 PUT 请求更新文件
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"文件已成功更新！")
    else:
        print(f"更新文件时发生错误: {response.status_code} - {response.text}")

# 主程序
def main():
    # GitHub 上 JSON 文件的原始 URL
    json_url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}'

    # 定义匹配旧链接的正则表达式 (匹配 http://<数字>hsck.cc 格式)
    old_link_pattern = r'http://\d+hsck\.cc'

    # 下载 valid_links.txt 中的所有新链接
    new_links = download_valid_links()
    if not new_links:
        print("没有有效链接可用.")
        return

    # 打印新链接列表供调试
    print("从 GitHub 下载的新链接列表:", new_links)

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, old_link_pattern, new_links)
    print("替换后的 JSON 数据：", json.dumps(updated_data, indent=2, ensure_ascii=False))  # 调试用

    # 获取文件的 SHA 值
    sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)
    if sha is None:
        return

    # 更新 JSON 文件
    update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

# 运行主程序
if __name__ == "__main__":
    main()
