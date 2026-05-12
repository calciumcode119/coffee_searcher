import json
import requests
from dotenv import load_dotenv
import os
from geopy import distance
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coffee_shops():
    with open('coffee.json', 'r', encoding='cp1251') as coffee:
        coffee_j = coffee.read()
    coffee_shops = json.loads(coffee_j)
    return coffee_shops


def get_coords(position):
    load_dotenv()
    apikey = os.environ['API_KEY']
    coords = fetch_coordinates(apikey, position)
    coords_swapped = coords[1], coords[0]
    return coords_swapped


def get_shop_distance(shop):
    return shop['distance']


def get_nearest_shops(coffee_shops, current_coords):
    shops_list = []

    for shop in coffee_shops:
        shop_info = {
        'title': ' ',
        'distance': 0.0,
        'latitude': 0.0,
        'longitude': 0.0,
        }
        
        shop_coords = shop['geoData']['coordinates']
        shop_coords_swapped = shop_coords[1], shop_coords[0]

        distance_to_shop = distance.distance(current_coords, shop_coords_swapped).km

        shop_info['title'] = shop['Name']
        shop_info['distance'] = distance_to_shop
        shop_info['latitude'] = shop_coords[1]
        shop_info['longitude'] = shop_coords[0]

        shops_list.append(shop_info)

    nearest_shops = sorted(shops_list, key=get_shop_distance)[:5]
    return nearest_shops


def create_map(current_coords, nearest_shops):
    coffee_map = folium.Map(location=(current_coords))

    for shop in nearest_shops:
        folium.Marker(
            location=[shop['latitude'], shop['longitude']],
            tooltip=shop['title'],
            popup='Расстояние: {}'.format(shop['distance']),
            icon=folium.Icon(color='green'),
        ).add_to(coffee_map)

    coffee_map.save('index.html')


def main():
    current_position = input('Где вы находитесь? ')
    current_coords = get_coords(current_position)
    coffee_shops = get_coffee_shops()
    nearest_shops = get_nearest_shops(coffee_shops, current_coords)

    print('Ваши координаты: ', current_coords)
    pprint(nearest_shops)
    create_map(current_coords, nearest_shops)


if __name__ == '__main__':
    main()
