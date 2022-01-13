import json
from configs import CITY
import requests


def get(url, header=None, proxy=None):
    try:
        response = requests.get(url, headers=header, proxies=proxy)
    except requests.HTTPError:
        return None
    return response


def get_data():
    with open('divar_cities.json') as f:
        cities = json.load(f)
    city_id = cities.get(CITY)

    response = get(f'https://api.divar.ir/v5/places/cities/{city_id}/districts')
    districts = json.loads(response.text)['districts']
    data = []
    for district in districts:
        name = district['name']
        subs = ' , '.join([tag['title'] for tag in district['tags']])
        if subs:
            data.append(f'{name} ({subs})')
        else:
            data.append(name)

    return city_id, data

