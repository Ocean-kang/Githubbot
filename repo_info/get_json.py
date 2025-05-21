import json

txt_file_path = "./repo_info/repo_address.txt"
output_path = "./repo_info/repo_web_whole.json"

with open(txt_file_path, "r", encoding="utf-8") as f:
    lines = [line.rstrip('\n') for line in f]

lines += [''] * (38 - len(lines)) if len(lines) < 38 else []

data = {}
for idx in range(38):
    key = str(idx + 1)
    value = lines[idx] if idx < len(lines) else ''
    data[key] = value

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("成功生成JSON文件")