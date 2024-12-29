import json

# 替换函数
def replace_links_in_json(json_file_path, old_link, new_link):
    try:
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

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

        # 保存修改后的 JSON 文件
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"所有包含 {old_link} 的链接已被替换为 {new_link}")

    except Exception as e:
        print(f"发生错误: {e}")

# 示例调用
json_file = 'https://github.com/hjpwyb/yuan/blob/main/tv/XYQHiker/%E5%AD%97%E5%B9%95%E4%BB%93%E5%BA%93.json'  # 请替换为实际文件路径
old_link = 'ck.cc'  # 要替换的旧链接
new_link = '7474ck.cc'  # 新的链接

replace_links_in_json(json_file, old_link, new_link)
