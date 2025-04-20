import re
import json

import yaml
from omegaconf import OmegaConf

WEBPATH = "./configs/repo_web.json"
YAMLPATH = "./configs"

def load_repoweb(path:str):
    with open(path, "r") as f:
        data = json.load(f)

    return data

def parse(url:str):
    pattern = r"https://github\.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    if match:
        owner = match.group(1)
        project_name = match.group(2)
    else:
        print("No match found")
    return_dict = dict()
    return_dict['owner'] = owner
    return_dict['project'] = project_name
    return return_dict

def writeconfig(cfgdict:dict):
    # open example config.yaml
    cfg = OmegaConf.load(YAMLPATH + '\config.yaml')
    # make a new dict for each repo'config.yaml
    res_dict = dict()
    res_dict['github'] = dict()
    res_dict['github']['GITHUB_TOKEN'] = cfg.github.GITHUB_TOKEN
    res_dict['github']['PER_PAGE'] = cfg.github.PER_PAGE
    res_dict['github']['REPO_OWNER'] = cfgdict['owner']
    res_dict['github']['REPO_NAME'] = cfgdict['project']
    with open(f"{YAMLPATH}/{cfgdict['project']}.yaml", "w") as file:
        yaml.dump(res_dict, file, allow_unicode=True, sort_keys=False)
    return None


def main():
    webs_dict = load_repoweb(WEBPATH)
    for idx, val in enumerate(webs_dict):
        web = webs_dict[val]
        res = parse(web)
        writeconfig(res)
    return None

if __name__ == "__main__":
    main()
