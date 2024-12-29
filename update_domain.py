import requests
import os
import base64
import json
from urllib.parse import urlparse

# GitHub 配置
GITHUB_TOKEN = os.getenv('YOU_TOKEN')  # 从环境变量中获取 GitHub Token
REPO_OWNER = 'hjpwyb'  # 仓库拥有者
REPO_NAME = 'yuan'  # 仓库名称
BRANCH_NAME = 'main'  # 分支名称
FILE_PATH = 'valid_links.txt'  # 要上传的文件路径
COMMIT_MESSAGE = '更新有效链接'  # 提交信息

# 尝试访问指定网址并返回有效性
def check_url(url):
    try:
        response = requests.get(url, timeout=10)  # 设置超时为 10 秒
        if response.status_code == 200:
            # 检查页面内容是否包含指定文本
            if "24小时在线匹配首次免费" in response.text:
                print(f"Valid domain found with matching content: {url}")
                return url
            else:
                print(f"Invalid domain (content mismatch): {url} (Status code: {response.status_code})")
                return None
        else:
            print(f"Invalid domain (Status code: {response.status_code}): {url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return None

# 获取文件的 SHA 值
def get_file_sha(repo_owner, repo_name, file_path, branch):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        return file_info['sha']
    elif response.status_code == 404:
        print(f"文件 {file_path} 不存在，准备创建新文件。")
        return None
    else:
        print(f"无法获取文件 SHA 值: {response.status_code}")
        return None

# 更新 GitHub 上的文件内容
def update_github_file(repo_owner, repo_name, file_path, new_data, sha, branch, commit_message):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 重新格式化文件内容
    formatted_content = "\n".join(new_data)

    # 将内容编码为 base64
    encoded_content = base64.b64encode(formatted_content.encode('utf-8')).decode('utf-8')
    
    # 构建请求体
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": branch
    }

    if sha:  # 如果文件存在，则需要提供 sha 来更新
        data["sha"] = sha
    
    # 发送 PUT 请求更新文件
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"文件已成功更新！")
    else:
        print(f"更新文件时发生错误: {response.status_code} - {response.text}")

# 主程序
def main():
    base_url = "http://7465ck.cc/vodtype/9-2.html"  # 要测试的基本 URL
    valid_links = []  # 存储有效链接

    # 进行试错，依次更换URL中的数字部分
    for i in range(7465, 8000):  # 假设你想测试7465ck.cc到7999ck.cc这几个域名
        url_to_test = base_url.replace("7465ck.cc", f"{i}ck.cc")
        
        # 检查URL有效性并匹配内容
        valid_url = check_url(url_to_test)
        if valid_url:
            # 只提取域名部分，不包括路径
            domain = urlparse(valid_url).scheme + "://" + urlparse(valid_url).hostname
            valid_links.append(domain)  # 如果链接有效，添加到有效链接列表

    if valid_links:
        # 获取现有文件的 SHA 值
        sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)

        # 更新 GitHub 上的文件
        update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, valid_links, sha, BRANCH_NAME, COMMIT_MESSAGE)
    else:
        print("没有找到有效的链接。")

# 运行主程序
if __name__ == "__main__":
    main()
