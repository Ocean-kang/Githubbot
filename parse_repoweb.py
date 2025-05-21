import re
import json

import yaml
from omegaconf import OmegaConf

REPOPATH = "./repo_info"
WEBPATH = "./repo_info/repo_web_whole.json"
YAMLPATH = "./configs"

def load_repoweb(path:str):
    with open(path, "r") as f:
        data = json.load(f)
    return data

def parse(url:str, key:str):
    pattern_github = r"https://github\.com/([^/]+)/([^/]+)"
    pattern_gitee = r"https://gitee\.com/([^/]+)/([^/]+)"
    match_github = re.match(pattern_github, url)
    match_gitee = re.match(pattern_gitee, url)
    if match_github:
        platform = 'github'
        owner = match_github.group(1)
        project_name = match_github.group(2)
    elif match_gitee:
        platform = 'gitee'
        owner = match_gitee.group(1)
        project_name = match_gitee.group(2)
    else:
        print("No match found")
    return_dict = dict()
    return_dict['owner'] = owner
    return_dict['project'] = project_name
    return_dict['group'] = key
    return_dict['platform'] = platform
    return return_dict

def writeconfig(cfgdict:dict):
    # open example config.yaml
    cfg = OmegaConf.load(YAMLPATH + r'\template\config.yaml')
    # make a new dict for each repo'config.yaml
    res_dict = dict()
    res_dict['github'] = dict()
    res_dict['github']['PER_PAGE'] = cfg.github.PER_PAGE
    res_dict['github']['REPO_OWNER'] = cfgdict['owner']
    res_dict['github']['REPO_NAME'] = cfgdict['project']
    res_dict['github']['GROUP'] = cfgdict['group']
    res_dict['github']['PLATFORM'] = cfgdict['platform']
    with open(f"{YAMLPATH}/tmp/{cfgdict['group']}.yaml", "w") as file:
        yaml.dump(res_dict, file, allow_unicode=True, sort_keys=False)
    return None

def write_repo_list(repolist:list):
    try:
        with open(REPOPATH+"/repo_list.txt", 'w') as f:
            for item in repolist:
                f.write(str(item) + '\n')
        print('Repo.txt writing successfully!')
    except Exception as e:
        print(f"Error in writing : {e}")

def main():
    webs_dict = load_repoweb(WEBPATH)
    repolist = list()
    for idx, val in enumerate(webs_dict):
        web = webs_dict[val]
        res = parse(web, val)
        writeconfig(res)
        repolist.append(res['project'])
    write_repo_list(repolist)
    return None

if __name__ == "__main__":
    main()
