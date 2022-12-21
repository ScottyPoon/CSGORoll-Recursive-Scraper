import json
import requests
import time
from google_currency import convert
from github import Github
import base64


# TODO: If prices are an hour old do something

# For fetching files >1MB from Github
def get_blob_content(repo, branch, path_name):
    # first get the branch reference
    ref = repo.get_git_ref(f'heads/{branch}')
    # then get the tree
    tree = repo.get_git_tree(ref.object.sha, recursive='/' in path_name).tree
    # look for path in tree
    sha = [x.sha for x in tree if x.path == path_name]
    if not sha:
        # well, not found..
        return None
    # we have sha
    return repo.get_git_blob(sha[0])


# Gets prices directly from buff163
def get_buff_price(name):
    try:
        buff_id = buff_ID_Dict[name]
        url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={buff_id}&_={time.time()}"
        try:
            response = requests.get(url)
            status = response.status_code
            while status != 200:  # Error codes 429, 403
                delay = 0.3
                time.sleep(delay)
                response = requests.get(url)
                status = response.status_code

            data = response.json()
            if len(data['data']['items']) < 9: return 0

            lowest_price = data['data']['items'][0]['price']

            return float(lowest_price)
        except IndexError:
            return 0
        except Exception:
            return 0
    except KeyError as e:
        print(f'I got a KeyError - reason {e}')
        return 0


# Gets prices from github repository, if it can't find the item then check buff163
def check_price(name):
    try:
        return pricempire_prices[name]
    except KeyError:
        try:
            return get_buff_price(name)
        except KeyError as e:
            print(f'I got a KeyError - reason {e}')
            return 0


# Convert USD to CNY
def usd_to_cny():
    g = convert('usd', 'cny', 100)

    res = ''.join(filter(lambda i: i.isdigit(), g))
    oneusdtormb = int(res) / 10000
    return oneusdtormb


# Get the amount of times the item is listed on buff163
def get_buff_amount(name):
    if "Doppler" and "Factory New" in name:
        return 10

    try:
        buff_id = buff_ID_Dict[name]
        url = f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={buff_id}&_={time.time()}"
        try:
            response = requests.get(url)
            status = response.status_code
            while status != 200:  # Error codes 429, 403
                delay = 0.3
                time.sleep(delay)
                response = requests.get(url)
                status = response.status_code

            data = response.json()

            return len(data['data']['items'])

        except IndexError:
            return 0
        except Exception:
            return 0
    except KeyError as e:
        print(f'I got a KeyError for amount - reason {e}')
        return 0


token = "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"
repo_name = "buff-prices"
github = Github(token)
repository = github.get_user().get_repo(repo_name)
pricempire_prices = json.loads(repository.get_contents("buff_prices.json").decoded_content.decode())
blob = get_blob_content(repository, "main", "buff_id.json")
b64 = base64.b64decode(blob.content)
buff_ID_Dict = json.loads(b64.decode("utf8"))
buff_ID_Dict = {v: k for k, v in buff_ID_Dict.items()}  # Swapping key value pair