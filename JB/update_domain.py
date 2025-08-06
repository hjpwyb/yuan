import requests
import os
import base64
from urllib.parse import urlparse

# GitHub 配置
GITHUB_TOKEN = os.getenv('YOU_TOKEN')
REPO_OWNER = 'hjpwyb'  # 仓库拥有者
REPO_NAME = 'yuan'  # 仓库名称
BRANCH_NAME = 'main'  # 分支名称
FILE_PATH = 'JB/valid_links2.txt'  # 要上传的文件路径
COMMIT_MESSAGE = '更新有效链接'  # 提交信息

# 尝试访问指定网址并返回有效性
def check_url(url):
    try:
        response = requests.get(url, timeout=10)  # 设置超时为 10 秒
        if response.status_code == 200:
            # 检查页面内容是否包含指定文本
            if "动漫剧情" in response.text:
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

# 更新 GitHub 上的文件内容（覆盖原文件）
def update_github_file(repo_owner, repo_name, file_path, new_data, sha, branch, commit_message):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # 重新格式化文件内容（每个链接占一行）
    formatted_content = "\n".join(new_data)  # 每个链接单独占一行

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
    if response.status_code in [200, 201]:
        print(f"文件已成功更新！")
    else:
        print(f"更新文件时发生错误: {response.status_code} - {response.text}")

# 主程序
def main():
    # 基本 URL，使用占位符来动态替换域名部分
    base_url_template = "http://{domain}/vodtype/9-2.html"  # 使用 {domain} 作为占位符
    valid_links = []  # 存储有效链接

    # 修改域名的范围，假设你想测试从6940ck.cc到6999ck.cc
    for i in range(8000, 8099):
        domain = f"{i}ck.cc"  # 动态生成新的域名
        url_to_test = base_url_template.format(domain=domain)  # 替换占位符
        print(f"Testing URL: {url_to_test}")  # 输出当前测试的 URL

        # 检查URL有效性并匹配内容
        valid_url = check_url(url_to_test)
        if valid_url:
            # 只提取域名部分，不包括路径
            domain = urlparse(valid_url).scheme + "://" + urlparse(valid_url).hostname
            valid_links.append(domain)  # 如果链接有效，添加到有效链接列表

    if valid_links:
        # 获取现有文件的 SHA 值
        sha = get_file_sha(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH_NAME)

        # 获取现有的有效链接（从 GitHub 上下载当前 valid_links.txt）
        current_links = []
        if sha:
            url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH_NAME}/{FILE_PATH}"
            response = requests.get(url)
            if response.status_code == 200:
                current_links = response.text.splitlines()

        # 更新链接：首先删除掉失效的旧网址
        updated_links = list(set(valid_links))  # 去重有效链接

        # 更新 GitHub 上的文件，覆盖原文件
        update_github_file(REPO_OWNER, REPO_NAME, FILE_PATH, updated_links, sha, BRANCH_NAME, COMMIT_MESSAGE)
    else:
        print("没有找到有效的链接。")

# 运行主程序
if __name__ == "__main__":
    main()
