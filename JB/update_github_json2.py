import json
import requests
import base64
import urllib.parse
import os

# GitHub 配置
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 从环境变量中获取 Token
REPO_OWNER = 'hjpwyb'
REPO_NAME = 'yuan'
FILE_PATH = 'tv/XYQHiker/黄色仓库.json'
BRANCH_NAME = 'main'
COMMIT_MESSAGE = '更新链接替换'
VALID_LINKS_FILE_PATH = 'JB/valid_links2.txt'  # 确保这里是 valid_links2.txt

# URL 编码文件路径
encoded_file_path = urllib.parse.quote(FILE_PATH)

# 下载 valid_links2.txt 中的所有新链接
def download_valid_links():
    url = f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{VALID_LINKS_FILE_PATH}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()  # 按行分割并返回链接列表
    except requests.exceptions.RequestException as e:
        print(f"下载 valid_links2.txt 时发生错误: {e}")
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

# 替换固定链接
def replace_fixed_links_in_json(data, new_link):
    # 直接替换包含固定链接的字段
    data['首页推荐链接'] = new_link
    data['首页片单链接加前缀'] = new_link
    data['分类链接'] = new_link + '/vodtype/{cateId}-{catePg}.html'  # 根据需要添加
    data['分类片单链接加前缀'] = new_link
    data['搜索链接'] = new_link + '/index.php/ajax/suggest?mid=1&wd={wd}'
    data['搜索片单链接加前缀'] = new_link + '/vodplay/'
    
    # 如果还需要替换其他字段，可以继续添加
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
    
    # 下载 valid_links2.txt 中的所有新链接
    new_links = download_valid_links()
    if not new_links:
        print("没有有效链接可用.")
        return

    # 打印下载的 valid_links2.txt 内容（调试用）
    print("=== 更新后的 valid_links2.txt 文件内容 ===")
    print("\n".join(new_links))

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 打印原始 JSON 数据（调试用）
    print("原始 JSON 数据：")
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # 替换链接
    updated_data = replace_fixed_links_in_json(data, new_links[0])  # 使用第一个新链接替换

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
