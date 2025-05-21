from datetime import datetime
import os
from pathlib import Path
import csv
import yaml

import httpx
import requests
from omegaconf import OmegaConf

CONFIG_PATH_SELF = './OYMK_configs/selfconfig.yaml'

CSV_COLUMNS = ['timestamp', 'user', 'commit_count', 'repo', 'branch', 'commit_message', 'commit_author']

def load_config(path:str):

    """Load config in OmegaConf class"""

    try:
        with open(path) as f:
            cfg = OmegaConf.load(path)
            print("Successful Loading the Config!")
            return cfg
    except FileNotFoundError:
        print(f"Error: File {path} not found !QAQ!")
        exit(1)
    except yaml.YAMLError as e:
        print(f"config file parse error: {str(e)}")
        exit(1)

cfg_self = load_config(CONFIG_PATH_SELF)

# Gitee API URL
url = "https://gitee.com/api/v5/repos/{owner}/{repo}"
# 替换为你的Gitee用户名和仓库名
url = url.format(owner="your_username", repo="your_repo_name")

url_test = 'https://gitee.com/qinghuan-in-the-afternoon/pickbay'

# 获取访问令牌（需要先在Gitee上生成）
headers = {
    "Authorization": cfg_self.github.GITEE_TOKEN
}

response = requests.get(url_test, headers=headers)
breakpoint()
if response.status_code == 200:
    repo_data = response.json()
    print(repo_data)
else:
    print(f"Failed to retrieve repository data: {response.status_code}")