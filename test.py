import json
import requests

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
def replace_links_in_json(data, old_link, new_link):
    # 遍历 JSON 数据，查找并替换链接
    def replace_in_dict(d):
        for key, value in d.items():
            if isinstance(value, str):  # 如果值是字符串
                if old_link in value:
                    d[key] = value.replace(old_link, new_link)
            elif isinstance(value, dict):  # 如果值是字典，递归替换
                replace_in_dict(value)
            elif isinstance(value, list):  # 如果值是列表，递归替换
                for item in value:
                    if isinstance(item, dict):
                        replace_in_dict(item)
                    elif isinstance(item, str):
                        if old_link in item:
                            item = item.replace(old_link, new_link)

    # 开始替换
    replace_in_dict(data)
    return data

# 保存修改后的 JSON 文件
def save_json_file(data, json_file_path):
    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"文件已保存为 {json_file_path}")
    except Exception as e:
        print(f"保存文件时发生错误: {e}")

# 主程序
def main():
    # GitHub 上 JSON 文件的原始 URL
    json_url = 'https://raw.githubusercontent.com/hjpwyb/yuan/main/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json'
    old_link = 'ck.cc'  # 要替换的旧链接
    new_link = '7474ck.cc'  # 新的链接

    # 下载 JSON 文件
    data = download_json_file(json_url)
    if data is None:
        return

    # 替换链接
    updated_data = replace_links_in_json(data, old_link, new_link)

    # 保存修改后的文件到本地
    save_json_file(updated_data, 'updated_file.json')

# 运行主程序
if __name__ == "__main__":
    main()
