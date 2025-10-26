import requests
from dotenv import dotenv_values
import yaml
import os

#  https://sl.bing.net/fTs3g1lmsy4

def list_group_members(group_id, bearer_token, qualtrics_base_url='iad1.qualtrics.com'):

    url = f"https://{qualtrics_base_url}/API/v3/groups/{group_id}/members"
    headers = {"x-api-token": f"bearer_token",
               "Content-Type": "application/json"
               }

    result = []
    while url is not None:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        result += data["result"]["elements"]
        url = data["result"]["nextPage"]

    return result

env_file = 'qualtrics_token'
if os.path.exists(env_file):
    envconfig = dotenv_values(env_file)

config_file = 'config_qualtrics.yaml'    
with open(config_file, 'r') as fp:
#try:
    cfg = yaml.safe_load(fp)
                
# Example usage
group_id = 'GR_0MSyUKRNqgwvaxE'
bearer_token = envconfig.get('QUALTRICS_APITOKEN')

group_members = list_group_members(group_id, bearer_token)
print(group_members)
