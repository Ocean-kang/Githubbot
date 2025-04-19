"""
GitHub仓库Push记录爬取及保存工具
功能：爬取指定仓库的push记录，保存时间、用户和提交信息到CSV文件
"""

import requests
import csv
import yaml
from datetime import datetime
from pathlib import Path
import os

# 配置文件路径
CONFIG_FILE = "github_config.yaml"

# CSV输出列定义
CSV_COLUMNS = ['timestamp', 'user', 'commit_message']

def load_config():
    """加载YAML配置文件"""
    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f)
            print("配置加载成功")
            return config
    except FileNotFoundError:
        print(f"错误：配置文件 {CONFIG_FILE} 不存在")
        exit(1)
    except yaml.YAMLError as e:
        print(f"配置文件解析错误：{str(e)}")
        exit(1)

def setup_proxies(proxy_config):
    """设置代理配置"""
    if not proxy_config.get('enabled', False):
        return None
    
    proxies = {}
    if proxy_config.get('http'):
        proxies['http'] = proxy_config['http']
    if proxy_config.get('https'):
        proxies['https'] = proxy_config['https']
    
    if proxies:
        print(f"代理已启用：{proxies}")
        return proxies
    return None

def fetch_github_events(config):
    """获取GitHub事件数据"""
    headers = {
        'Authorization': f'token {config["github"]["token"]}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'https://api.github.com/repos/{config["github"]["repo_owner"]}/{config["github"]["repo_name"]}/events'
    
    events = []
    page = 1
    per_page = 100  # GitHub允许的最大值
    
    print("开始获取Push事件...")
    
    while True:
        params = {'page': page, 'per_page': per_page}
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                proxies=setup_proxies(config.get('proxy', {})))
            
            # 处理响应状态
            if response.status_code != 200:
                print(f"请求失败，状态码：{response.status_code}")
                print(f"响应内容：{response.text[:200]}")
                break
                
            current_events = response.json()
            if not current_events:
                print("所有数据获取完成")
                break
                
            # 过滤并处理Push事件
            for event in current_events:
                if event['type'] == 'PushEvent':
                    for commit in event['payload']['commits']:
                        events.append({
                            'timestamp': datetime.strptime(
                                event['created_at'], 
                                '%Y-%m-%dT%H:%M:%SZ'
                            ).strftime('%Y-%m-%d %H:%M:%S'),
                            'user': event['actor']['login'],
                            'commit_message': commit['message'].strip().replace('\n', ' ')
                        })
            
            print(f"已获取第 {page} 页，累计 {len(events)} 条提交")
            page += 1
            
            # 检查速率限制
            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            if remaining < 10:
                print(f"剩余API请求次数:{remaining}，建议暂停")
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求失败：{str(e)}")
            break
    
    return events

def save_to_csv(data, filename):
    """保存数据到CSV文件"""
    if not data:
        print("没有数据需要保存")
        return
    
    # 创建输出目录
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(data)
            print(f"数据成功保存到：{output_path.absolute()}")
            print(f"记录总数：{len(data)}")
            
            # 显示样本数据
            print("\n示例数据: ")
            for i in range(min(3, len(data))):
                print(f"{data[i]['timestamp']} | {data[i]['user']} | {data[i]['commit_message'][:30]}...")
                
    except PermissionError:
        print(f"文件写入权限被拒绝：{filename}")
    except Exception as e:
        print(f"保存文件失败：{str(e)}")

def main():
    # 加载配置
    config = load_config()
    
    # 获取数据
    events = fetch_github_events(config)
    
    # 保存数据
    if events:
        output_file = config.get('output', {}).get('csv_path', 'github_events.csv')
        save_to_csv(events, output_file)
    else:
        print("未获取到有效数据")

if __name__ == '__main__':
    main()