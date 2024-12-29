name: Run Python Script

on:
  push:
    branches:
      - main
  workflow_dispatch:  # 手动触发工作流

jobs:
  run-python-script:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout the repository
        uses: actions/checkout@v3  # 检出代码库

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'  # 选择 Python 版本

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests  # 安装 requests 库（如果没有的话）

      - name: Run test.py
        run: python test.py  # 运行 test.py 脚本

      - name: Upload the modified file
        uses: actions/upload-artifact@v3
        with:
          name: modified-json
          path: downloaded_file.json  # 上传修改后的文件
