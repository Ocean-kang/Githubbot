import os
import requests
from tabulate import tabulate
from collections import defaultdict

# 配置GitHub访问令牌（可选但推荐）
GITHUB_TOKEN = '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'  # 替换为你的token或使用环境变量

def get_commits(owner, repo):
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    url = f'https://api.github.com/repos/{owner}/{repo}/commits'
    commits = []
    page = 1
    while True:
        params = {'page': page, 'per_page': 100}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        if not data:
            break
        commits.extend(data)
        page += 1
    return commits

def analyze_commits(commits):
    contributor_stats = defaultdict(int)
    commit_details = []
    for commit in commits:
        sha = commit['sha'][:7]
        author_info = commit.get('author', {})
        if author_info:
            author = author_info.get('login', 'Unknown')
        else:
            # 如果author字段为空，尝试从commit信息中获取
            commit_data = commit['commit']
            author = commit_data['author']['name']
        date = commit['commit']['author']['date']
        message = commit['commit']['message'].split('\n')[0]  # 取首行消息
        contributor_stats[author] += 1
        commit_details.append([sha, author, date, message])
    return contributor_stats, commit_details

def main():
    # 输入仓库信息
    repo_full_name = input("Enter GitHub repository (格式: owner/repo): ")
    owner, repo = repo_full_name.split('/')
    
    # 获取并分析提交
    commits = get_commits(owner, repo)
    stats, details = analyze_commits(commits)
    
    # 输出统计表
    stats_table = [[author, count] for author, count in stats.items()]
    print("\n贡献者提交统计:")
    print(tabulate(stats_table, headers=["Author", "Commits"], tablefmt="grid"))
    
    # 输出详细提交记录（可选）
    print("\n最近提交记录:")
    print(tabulate(details[:10], headers=["SHA", "Author", "Date", "Message"], tablefmt="grid"))

if __name__ == "__main__":
    main()