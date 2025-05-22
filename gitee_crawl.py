from datetime import datetime
import os
from pathlib import Path
import csv
import yaml

import httpx
from omegaconf import OmegaConf

CONFIG_PATH_SELF = './OYMK_configs/selfconfig.yaml'
CONFIG_DIR_PATH = './configs/tmp'
CSV_COLUMNS = ['timestamp', 'user', 'commit_count', 'repo', 'branch', 'commit_message', 'commit_author']

os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

def get_push_events(cfg_self, cfg):
    # 修改为Gitee API地址
    url = f'https://gitee.com/api/v5/repos/{cfg.github.REPO_OWNER}/{cfg.github.REPO_NAME}/events'
    
    # Gitee使用access_token作为查询参数
    params = {
        'access_token': cfg_self.github.GITEE_TOKEN,
        'page': 1,
        'per_page': cfg.github.PER_PAGE
    }

    results = []

    while True:
        # 发送带token参数的请求
        response = httpx.get(url, params=params)
        
        if response.status_code == 200:
            events = response.json()
            if not events:
                break

            for event in events:
                # Gitee的Push事件类型为'PushEvent'
                if event['type'] == 'PushEvent':
                    push_data = {
                        # 用户信息路径不同
                        'user': event['actor']['login'],
                        'timestamp': event['created_at'],
                        # commits数量在payload中直接获取
                        'commit_count': len(event['payload']['commits']),
                        'branch': event['payload']['ref'].split('/')[-1],
                        'repo': f"{cfg.github.REPO_OWNER}/{cfg.github.REPO_NAME}",
                    }
                    
                    # 处理commit信息
                    commits = event['payload']['commits']
                    for commit in commits:
                        push_data['commit_message'] = f"!{commit['message']}!"
                        # Gitee author信息结构不同
                        push_data['commit_author'] = f"!{commit['author']['name']}!"
                    results.append(push_data)
            
            # Gitee分页通过next page判断
            if 'next' in response.links:
                url = response.links['next']['url']
            else:
                break
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print(response.json())
            break

    return results

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

def save_to_csv(data, filename):
    """Save the data to a CSV file"""
    if not data:
        print("No valid data")
        return
    
    # 创建输出目录
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(data)
            print(f"Successfully saving: {output_path.absolute()}")
            print(f"Totally: {len(data)}")
              
    except PermissionError:
        print(f"The file write permission was denied: {filename}")
    except Exception as e:
        print(f"Save file error: {str(e)}")

def main():
    cfg_self = load_config(CONFIG_PATH_SELF)
    for config_name in os.listdir(CONFIG_DIR_PATH):
        cfg = load_config(os.path.join(CONFIG_DIR_PATH, config_name))
        # 修改平台判断条件
        if cfg['github']['PLATFORM'] == 'gitee':
            events = get_push_events(cfg_self, cfg)
            output_file = f"./output/{cfg.github.GROUP}.csv"
            save_to_csv(events, output_file)

if __name__ == '__main__':
    main()