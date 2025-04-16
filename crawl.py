from datetime import datetime
import os

import httpx
import requests
from omegaconf import OmegaConf

# 配置参数
cfg = OmegaConf.load('./config.yaml')
GITHUB_TOKEN = cfg.GITHUB_TOKEN
REPO_OWNER = cfg.REPO_OWNER
REPO_NAME = cfg.REPO_NAME
PER_PAGE = cfg.PER_PAGE

# 禁用代理
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''

def get_push_events():
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/events'
    
    page = 1
    results = []

    while True:
        params = {'page': page, 'per_page': PER_PAGE}
        response = httpx.get(url, headers=headers, params=params)
        
        # 处理API响应
        if response.status_code == 200:
            events = response.json()
            if not events:
                break  # 没有更多数据

            for event in events:
                if event['type'] == 'PushEvent':
                    push_data = {
                        'user': event['actor']['login'],
                        'timestamp': event['created_at'],
                        'commit_count': len(event['payload']['commits']),
                        'branch': event['payload']['ref'].split('/')[-1],
                        'repo': f"{REPO_OWNER}/{REPO_NAME}",
                        'commits': [{
                            'message': commit['message'],
                            'sha': commit['sha'][:7],
                            'author': commit['author']['name']
                        } for commit in event['payload']['commits']]
                    }
                    results.append(push_data)
            
            page += 1
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print(response.json())
            break

    return results

def format_output(events):
    for event in events:
        print(f"用户：{event['user']}")
        print(f"时间：{datetime.strptime(event['timestamp'], '%Y-%m-%dT%H:%M:%SZ')}")
        print(f"分支：{event['branch']}")
        print(f"提交数量：{event['commit_count']}")
        print("具体提交：")
        for commit in event['commits']:
            print(f"  SHA: {commit['sha']} | 作者: {commit['author']}")
            print(f"  信息: {commit['message'].splitlines()[0]}")
        print("-" * 50)

if __name__ == '__main__':
    push_events = get_push_events()
    format_output(push_events)
    print(f"共获取到 {len(push_events)} 条push记录")