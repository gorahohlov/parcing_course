import requests
from pprint import pprint
import json

username = 'gorahohlov'
token = '#############################'
user = input('Введите логин пользователя: ')
# user = 'dipanjanS'

# resp = requests.get('https://api.github.com/user', auth=(username, token))
resp = requests.get(f'https://api.github.com/users/{user}')#, auth=(username, token))

j_resp = resp.json()

# pprint(j_resp)
print()
print(f"Количество репозиториев: {j_resp.get('public_repos')}")
print(f"Ссылка на репозитории: {j_resp.get('repos_url')}")
print()
# получили информацию о пользователе (о себе) идем дальше

# repos = requests.get('https://api.github.com/user/repos', auth=(username, token))
repos = requests.get(f'https://api.github.com/users/{user}/repos')#, auth=(username, token))

# for repo in repos.json():
#     if not repo['private']:
#         print(repo['html_url'])
# print()
for repo in repos.json():
    if not repo['private']:
        s = repo['full_name']
        s = s[s.find('/')+1:]
        print(s)

print()
# pprint(repos.json())
# print(type(repos.json()))

with open('C:/Users/gorah/Documents/parcing_scraping/lesson01/repos_list.json', 'w') as f:
    json.dump(repos.json(), f)