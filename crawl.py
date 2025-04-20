from datetime import datetime
import os
from pathlib import Path
import csv
import yaml

import httpx
import requests
from omegaconf import OmegaConf

# 配置参数
CONFIG_PATH = './configs/config.yaml'
# CSV输出列定义
CSV_COLUMNS = ['timestamp', 'user', 'commit_count', 'repo', 'branch', 'commit_message', 'commit_author']

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

def get_push_events(cfg):
    headers = {
        'Authorization': f'token {cfg.github.GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{cfg.github.REPO_OWNER}/{cfg.github.REPO_NAME}/events'
    
    page = 1
    per_page = 100  # GitHub enable upper
    results = []

    while True:
        params = {'page': page, 'per_page': cfg.github.PER_PAGE}
        response = httpx.get(url, headers=headers, params=params)
        
        # deal with api reaction
        if response.status_code == 200:
            events = response.json()
            if not events:
                break

            for event in events:
                if event['type'] == 'PushEvent':
                    push_data = {
                        'user': event['actor']['login'],
                        'timestamp': event['created_at'],
                        'commit_count': len(event['payload']['commits']),
                        'branch': event['payload']['ref'].split('/')[-1],
                        'repo': f"{cfg.github.REPO_OWNER}/{cfg.github.REPO_NAME}",
                    }
                    for commit in event['payload']['commits']:
                        push_data['commit_message'] = f"!{commit['message']}!"
                        push_data['commit_author'] = f"!{commit['author']['name']}!"
                    results.append(push_data)
            
            page += 1
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

def setup_proxies(proxy_config):
    """set proxy"""
    if not proxy_config.proxy.enabled == ('false' or "False"):
        return None
    
    proxies = {}
    if proxy_config.proxy.http:
        proxies['http'] = proxy_config.proxy.http
    if proxy_config.proxy.https:
        proxies['https'] = proxy_config.proxy.https
    
    if proxies:
        print(f" proxy working:{proxies}")
        return proxies
    return None

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
    cfg = load_config(CONFIG_PATH)
    events = get_push_events(cfg)

    if events:
        output_file = f"./output/{cfg.github.REPO_NAME}.csv"
        save_to_csv(events, output_file)
    else:
        print("No valid data was obtained! ")

if __name__ == '__main__':
    main()