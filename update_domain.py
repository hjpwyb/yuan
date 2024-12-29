import requests

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

# 主程序
def main():
    base_url = "http://7465ck.cc/vodtype/9-2.html"  # 要测试的基本 URL

    # 进行试错，依次更换URL中的数字部分
    for i in range(7465, 7475):  # 假设你想测试7465ck.cc到7474ck.cc这几个域名
        url_to_test = base_url.replace("7465ck.cc", f"{i}ck.cc")
        
        # 检查URL有效性并匹配内容
        check_url(url_to_test)

if __name__ == "__main__":
    main()
