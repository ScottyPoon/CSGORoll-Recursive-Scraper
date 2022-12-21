import requests
import rmbprice
import json

url = 'https://api.csgoroll.com/graphql'

headers = {
    'User-Agent': 'Mozilla/5.0',
}

sort_list = []


def iterate_roll(end_cursor, min_price, max_price):
    last_item = None
    if end_cursor is None:
        params = {
            'operationName': 'TradeList',
            'variables': '{"first":250,"orderBy":"TOTAL_VALUE_DESC","status":"LISTED","steamAppName":"CSGO","marketName":null,"maxMarkupPercent":null}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"d7fc14483c28e5d48c91d1e4f1c93a0ed9781ff79dff64bfc5bf57da912a43a1"}}',
        }

        r = requests.get(url, headers=headers, params=params)
        print("Status Code", r.status_code)
        end_cursor = r.json()['data']['trades']['pageInfo']['endCursor']
        item_list = r.json()['data']['trades']['edges']
        for item in item_list:
            name = item['node']['tradeItems'][0]['marketName']
            if "Ruby" in name or "Sapphire" in name or "Black Pearl" in name:
                name = name.replace("|", "| Doppler")
            elif "Emerald" in name and "Gloves" not in name and "Desert" not in name and "P90" not in name and "CZ75-Auto" not in name and "AK-47" not in name:
                name = name.replace("|", "| Gamma Doppler")
            price = item['node']['tradeItems'][0]['value']

            div = rmbprice.check_price(name) / price
            # markup_percentage = item['node']['markupPercent']
            tup = div, name, price

            if last_item == tup:
                continue
            else:
                last_item = tup
            if price > max_price:
                continue
            print("{0:<60} {1}".format(name, price))
            sort_list.append(tup)

        return iterate_roll(end_cursor, min_price, max_price)

    elif end_cursor is not None:

        params = {
            'operationName': 'TradeList',
            'variables': '{{"first":250,"orderBy":"TOTAL_VALUE_DESC","status":"LISTED","steamAppName":"CSGO","marketName":null,"maxMarkupPercent":null,"after":"{0}"}}'.format(
                end_cursor),
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"d7fc14483c28e5d48c91d1e4f1c93a0ed9781ff79dff64bfc5bf57da912a43a1"}}',
        }

        r = requests.get(url, headers=headers, params=params)
        print("NEXT PAGE")
        end_cursor = r.json()['data']['trades']['pageInfo']['endCursor']
        item_list = r.json()['data']['trades']['edges']
        for item in item_list:
            name = item['node']['tradeItems'][0]['marketName']
            if "Ruby" in name or "Sapphire" in name or "Black Pearl" in name:
                name = name.replace("|", "| Doppler")
            elif "Emerald" in name and "Gloves" not in name and "Desert" not in name and "P90" not in name and "CZ75-Auto" not in name and "AK-47" not in name:
                name = name.replace("|", "| Gamma Doppler")
            price = item['node']['tradeItems'][0]['value']

            if price > max_price:
                continue

            if price < min_price:
                return True
            div = rmbprice.check_price(name) / price
            # markup_percentage = item['node']['markupPercent']
            tup = div, name, price

            if last_item == tup:
                continue
            else:
                last_item = tup
            print("{0:<60} {1}".format(name, price))
            sort_list.append(tup)

        return iterate_roll(end_cursor, min_price, max_price)


def output_sorted_list(sort_list, number):
    items_dict = {}
    for item in sort_list:
        items_dict[item[1]] = (item[0], item[2])  # key = name, item0 = div, item 2 = price

    if number == 1:
        sorted_tuples = sorted(items_dict.items(), key=lambda item: item[1])  # Sort Dictionary Using a Lambda Function
    elif number == 2:
        sorted_tuples = sorted(items_dict.items(), key=lambda item: item[1], reverse=True)

    sorted_dict = {k: v for k, v in sorted_tuples}  # sorted function returns list so convert list to dict

    if number == 1:
        top_quarter = dict(list(sorted_dict.items())[int(len(sorted_dict) * .75): len(sorted_dict)])  # Slice dictionary
        print(" Top 25 Percentile")
        for k, (v1, v2) in top_quarter.items():
            print("{0:.2f} {1:60} {2:.2f}".format(v1, k, v2))
    elif number == 2:
        top_quarter = sorted_dict

    print("\n SORTING NEWLIST \n")
    illiquid = []
    liquid = []
    doppler = []
    sticker = []
    souvenir = []
    count = 0
    newListLen = len(top_quarter)
    for k, (v1, v2) in top_quarter.items():
        item = v1, k, v2
        if "Doppler" in k:
            doppler.append(item)
        elif "Sticker" in k or "Dreamhack 2014 Legends" in k:
            amount = rmbprice.get_buff_amount(k)
            item = v1, k, v2, amount
            sticker.append(item)
        elif "Souvenir" in k:
            souvenir.append(item)
        else:
            amount = rmbprice.get_buff_amount(k)
            if amount < 10:
                illiquid.append(item)
            else:
                liquid.append(item)
        print(f"{count}/{newListLen}")
        count = count + 1

    print("\n Souvenir \n")
    for item in souvenir:
        print("{0:.2f} {1:60} {2:.2f}".format(item[0], item[1], item[2]))

    print("\n Illiquid \n")
    for item in illiquid:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))

    print("\n Sticker \n")
    for item in sticker:
        print("{0:.2f} {1:<60} {2:.2f} {3}".format(item[0], item[1], item[2], item[3]))

    print("\n Doppler \n")
    for item in doppler:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))

    print("\n Liquid \n")
    for item in liquid:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))


def iterate_roll_crash(end_cursor, min_value, max_value, multiplier):
    last_item = None
    if end_cursor is None:
        params = {
            'operationName': 'ItemVariantList',
            'variables': '{"first":250,"orderBy":"VALUE_DESC","distinctValues":true,"usable":true,"obtainable":true,"withdrawable":true}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"f52769449b71d7e80961cc95fd22a368eb309a40442809953b9181d3428cfa03"}}',
        }

        r = requests.get(url, headers=headers, params=params)

        end_cursor = r.json()['data']['itemVariants']['pageInfo']['endCursor']
        item_list = r.json()['data']['itemVariants']['edges']
        for item in item_list:
            name = item['node']['externalId']
            if "Ruby" in name or "Sapphire" in name or "Black Pearl" in name:
                name = name.replace("|", "| Doppler")
            elif "Emerald" in name and "Gloves" not in name and "Desert" not in name and "P90" not in name and "CZ75-Auto" not in name and "AK-47" not in name:
                name = name.replace("|", "| Gamma Doppler")
            price = item['node']['value']

            if price > max_value:
                continue

            price = price * multiplier

            div = rmbprice.check_price(name) / price
            tup = div, name, price

            if last_item == tup:
                continue
            else:
                last_item = tup

            print("{0:<59} {1:.2f}".format(name, price))
            sort_list.append(tup)

        return iterate_roll_crash(end_cursor, min_value, max_value, multiplier)

    elif end_cursor is not None:

        params = {
            'operationName': 'ItemVariantList',
            'variables': '{{"first":250,"orderBy":"VALUE_DESC","distinctValues":true,"usable":true,"obtainable":true,"withdrawable":true,"after":"{0}"}}'.format(
                end_cursor),
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"d7fc14483c28e5d48c91d1e4f1c93a0ed9781ff79dff64bfc5bf57da912a43a1"}}',
        }
        r = requests.get(url, headers=headers, params=params)
        print("NEXT PAGE")
        end_cursor = r.json()['data']['itemVariants']['pageInfo']['endCursor']
        item_list = r.json()['data']['itemVariants']['edges']
        for item in item_list:
            name = item['node']['externalId']
            if "Ruby" in name or "Sapphire" in name or "Black Pearl" in name:
                name = name.replace("|", "| Doppler")
            elif "Emerald" in name and "Gloves" not in name and "Desert" not in name and "P90" not in name and "CZ75-Auto" not in name and "AK-47" not in name:
                name = name.replace("|", "| Gamma Doppler")
            price = item['node']['value']

            if price > max_value:
                continue

            if price < min_value:
                return True

            price = price * multiplier

            div = rmbprice.check_price(name) / price
            tup = div, name, price

            if last_item == tup:
                continue
            else:
                last_item = tup
            print("{0:<59} {1:.2f}".format(name, price))
            sort_list.append(tup)
        return iterate_roll_crash(end_cursor, min_value, max_value, multiplier)


def output_sorted_list2(sort_list):
    items_dict = {}
    for item in sort_list:
        items_dict[item[1]] = (item[0], item[2])  # key = name, item0 = div, item 2 = price

    sorted_tuples = sorted(items_dict.items(), key=lambda item: item[1],
                           reverse=True)  # Sort Dictionary Using a Lambda Function

    sorted_dict = {k: v for k, v in sorted_tuples}  # sorted function returns list so convert list to dict

    print("\n SORTING NEWLIST \n")
    illiquid = []
    liquid = []
    doppler = []
    sticker = []
    souvenir = []
    count = 0
    newListLen = len(sorted_dict)
    for k, (v1, v2) in sorted_dict.items():
        item = v1, k, v2
        if "Doppler" in k:
            doppler.append(item)
        elif "Sticker" in k or "Dreamhack 2014 Legends" in k:
            amount = rmbprice.get_buff_amount(k)
            item = v1, k, v2, amount
            sticker.append(item)
        elif "Souvenir" in k:
            souvenir.append(item)
        else:
            amount = rmbprice.get_buff_amount(k)
            if amount < 10:
                illiquid.append(item)
            else:
                liquid.append(item)
        print(f"{count}/{newListLen}")
        count = count + 1

    print("\n Souvenir \n")
    for item in souvenir:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))

    print("\n Illiquid \n")
    for item in illiquid:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))

    print("\n Sticker \n")
    for item in sticker:
        print("{0:.2f} {1:<60} {2:.2f} {3}".format(item[0], item[1], item[2], item[3]))

    print("\n Doppler \n")
    for item in doppler:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))

    print("\n Liquid \n")
    for item in liquid:
        print("{0:.2f} {1:<60} {2:.2f}".format(item[0], item[1], item[2]))


def scrape_inventory():
    inventory_list = []

    last_name = None
    end_cursor = None
    with open("inventory.json", 'r') as filein:
        data = json.load(filein)['data']['inventoryItemVariants']['steamItems']
        max_price = data[0]['itemVariant']['value'] * 1.12

        for items in data:
            name = items['itemVariant']['externalId']
            if "Ruby" in name or "Sapphire" in name or "Black Pearl" in name:
                name = name.replace("|", "| Doppler")
            if last_name == name:
                continue
            else:
                last_name = name

            price = items['itemVariant']['value']

            if price < 35:
                break

            min_price = price * 1.12

            tup = name, price
            inventory_list.append(tup)

        iterate_roll(end_cursor, min_price, max_price)

        items_dict = {}
        for item in sort_list:
            items_dict[item[1]] = (item[0], item[2])  # key = name, item0 = div, item 2 = price

        markup_list = []
        markup_list_sorted = []

        for k, (v1, v2) in items_dict.items():
            for i, item in enumerate(inventory_list):
                name = item[0]
                price = item[1]
                if name == k:
                    markup = (v2 - price) / price * 100
                    tup = markup, name, price
                    markup_list.insert(i, tup)

        not_found = []
        for i_item in inventory_list:
            flag = False
            for m_item in markup_list:
                if i_item[0] == m_item[1]:
                    flag = True
            if not flag:
                tup = 12, i_item[0], i_item[1]
                not_found.append(tup)

        completed_list = markup_list + not_found

        for item in completed_list:
            markup = item[0]
            name = item[1]
            price = item[2]
            markup_multiplier = 1 + markup / 100
            price = markup_multiplier * price
            div = rmbprice.check_price(name) / price
            tup = div, name, price, markup
            markup_list_sorted.append(tup)

        markup_list_sorted.sort(key=lambda x: x[0], reverse=True)
        for item in markup_list_sorted:
            print("{0:.2f} {1:<60} {2:<8} {3:.2f}".format(item[0], item[1], round(item[2], 2), item[3]))


n_input = input("[1] Scrape CSGORoll\n[2] Scrape items to Deposit\n[3] Scrape CS:GO Inventory\n")
try:
    n_input = int(n_input)
except:
    print("An exception occurred")
    quit()

end_cursor = None

if n_input == 1:
    min_price = int(input("Enter Minimum Price "))
    max_price = int(input("Enter Maximum Price "))
    iterate_roll(end_cursor, min_price, max_price)
    output_sorted_list(sort_list, n_input)
elif n_input == 2:
    min_value = int(input("Enter Minimum Price "))
    max_value = int(input("Enter Maximum Price "))
    multiplier = 1.095
    print("multiplier is", multiplier)
    iterate_roll_crash(end_cursor, min_value, max_value, multiplier)
    output_sorted_list(sort_list, n_input)
elif n_input == 3:
    scrape_inventory()
else:
    print("Not Valid Command")
# Combine output_sorted_list functions
# Make inventory scrape function, optional to login to steam
