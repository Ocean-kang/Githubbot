import requests

# Gitee API URL
url = "https://gitee.com/api/v5/repos/{owner}/{repo}"
# 替换为你的Gitee用户名和仓库名
url = url.format(owner="your_username", repo="your_repo_name")

# 获取访问令牌（需要先在Gitee上生成）
headers = {
    "Authorization": "token YOUR_ACCESS_TOKEN"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    repo_data = response.json()
    print(repo_data)
else:
    print(f"Failed to retrieve repository data: {response.status_code}")