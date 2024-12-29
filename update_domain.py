import requests

# 尝试访问指定网址并返回有效性
def check_url(url):
    try:
        response = requests.get(url, timeout=10)  # 设置超时为 10 秒
        if response.status_code == 200:
            print(f"Valid domain found: {url}")
            return url  # 返回有效的 URL
        else:
            print(f"Invalid domain: {url} (Status code: {response.status_code})")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Failed to access {url}: {e}")
        return None

# 主程序
def main():
    base_url = "http://7465ck.cc/vodtype/9-2.html"  # 要测试的基本 URL

    # 进行试错，依次更换URL中的数字部分
    for i in range(7465, 7470):  # 假设你想测试7465ck.cc到7470ck.cc这几个域名
        url_to_test = base_url.replace("7465ck.cc", f"{i}ck.cc")
        
        # 检查URL有效性
        valid_url = check_url(url_to_test)
        if valid_url:
            # 找到有效域名后，打印结果
            print(f"Found valid URL: {valid_url}")
            # 这里可以添加后续操作，比如获取 JSON 文件并推送更新等
            # 如果你需要后续处理，可以调用其他函数来执行
            break  # 找到有效的 URL 后停止进一步试错

if __name__ == "__main__":
    main()
