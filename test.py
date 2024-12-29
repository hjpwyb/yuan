import json
import requests
import base64
import os
import re  # 导入正则表达式库
import urllib.parse

# 获取 GitHub Token 从环境变量
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 从环境变量获取 YOU_TOKEN
REPO_OWNER = 'hjpwyb'  # 仓库拥有者
REPO_NAME = 'yuan'  # 仓库名称
FILE_PATH = urllib.parse.unquote('tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json')  # 解码文件路径
BRANCH_NAME = 'main'  # 分支名称
COMMIT_MESSAGE = '更新链接替换'  # 提交信息

# 下载 GitHub 上的原始文件内容
def download_json_file(url):
    try:
        # 获取文件的原始内容
        response = requests.get(url)
        response.raise_for_status()  # 确保请求成功
        return response.json()  # 返回解析的 JSON 数据
    except requests.exceptions.RequestException as e:
        print(f"下载文件时发生错误: {e}")
        return None

# 替换函数
def replace_links_in_json(data, old_link_pattern, new_link):
    # 遍历 JSON 数据，查找并替换链接
    def replace_in_dict(d):
        for key, value in d.items():
            if isinstance(value, str):  # 如果值是字符串
                # 使用正则表达式匹配 old_link_pattern
                if re.search(old_link_pattern, value):  # 查找包含数字的旧链接
                    d[key] = re.sub(old_link_pattern, new_link, value)  # 替换为新链接
            elif isinstance(value, dict):  # 如果值是字典，递归替换
                replace_in_dict(value)
            elif isinstance(value, list):  # 如果值是列表，递归替换
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        replace_in_dict(item)
                    elif isinstance(item, str):
                        if re.search(old_link_pattern, item):  # 查找并替换
                            value[i] = re.sub(old_link_pattern, new_link, item)

    # 开始替换
    replace_in_dict(data)
    return data

# 获取文件的 SHA 值
def get_file_sha(repo_owner, repo_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    print(response.status_code, response.text)  # 打印状态码和返回文本
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
    
    # 将新数据转换为 base64 编码
    encoded_content = base64.b64encode(json.dumps(new_data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    
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
    json_url = 'https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json'
    old_link = r'\d{4}ck\.cc'  # 用正则表达式匹配包含数字的链接，例如 7465ck.cc
    new_link = '7474ck.cc'  # 新的链接

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, old_link, new_link)

    # 获取文件的 SHA 值
    sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)
    if sha is None:
        return

    # 更新文件
    update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, updated_data, sha, BRANCH_NAME, COMMIT_MESSAGE)

# 运行主程序
if __name__ == "__main__":
    main()
