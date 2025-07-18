#!env python3

import os
import sys
import http.client
import urllib.parse
import argparse
import json

class digital_blasphemy_wallpaper:
    def __init__(self, id:int, name:str, all_free:bool, content:str, free:bool, paths:dict, rating:float, resolutions:dict):
        self.id = id
        self.name = name
        self.all_free = all_free
        self.content = content
        self.free = free
        self.paths = paths
        self.rating = rating
        self.resolutions = resolutions

    def get_wallpaper(self, screens:str, width:int, height:int):
        if screens not in self.resolutions:
            return None

        wp = None
        for s in self.resolutions[screens]:
            if s['width'] == width and s['height'] == height:
                wp = s
                break

        return wp


class digital_blasphemy_account:
    def __init__(self, active:bool, display_name:str, id:int, lifetime:bool, plus:bool, membership_level=None):
        self.active = active
        self.display_name = display_name
        self.id = id
        self.lifetime = lifetime
        self.plus = plus
        self.membership_level = membership_level

class digital_blasphemy:
    API_BASE = 'api.digitalblasphemy.com'
    def __init__(self, api_key:str):
        self.api_key = api_key

    def response(self, url, payload=None, headers=None, query_args=None):
        conn = http.client.HTTPSConnection(digital_blasphemy.API_BASE)
        method = 'GET'

        if payload:
            method = 'POST'

        if not payload:
            payload = ''

        if headers:
            headers = headers | {
                                    'Accept': 'application/json',
                                    'Authorization': f'Bearer {self.api_key}'
                                }
        if not headers:
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }

        if query_args:
            url = f'{url}?{dict_to_query_str(query_args)}'

        conn.request(method, url, payload, headers)
        response = conn.getresponse()
        data = response.read()
        parsed_data = json.loads(data)
        return parsed_data

    def get_file(self, url, filename):
        parsed_url = urllib.parse.urlparse(url)

        proto = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port or (443 if proto == 'https' else 80)

        path = parsed_url.path
        query = parsed_url.query

        recon_path = f'{path}?{query}'

        print(f'get_file - host: {host}, port: {port}, path: {recon_path}')

        headers = { 'Authorization': f'Bearer {self.api_key}' }
        headers = {}

        conn = http.client.HTTPSConnection(f'{host}:{port}')
        conn.request('GET', recon_path, headers=headers)
        response = conn.getresponse()
        response_code = response.getcode()
        print(f'get_file - response: {response_code}')
        if response_code == http.client.OK:
            data = response.read()
            with open(filename, 'wb') as f:
                f.write(data)
                return True

        return False

    def init(self) -> bool:
        summary = self.get_summary()
        if not summary:
            return False

        if 'db_core' not in summary:
            print('Failed to find db_core in summary')
            return False

        db_core = summary['db_core']

        if 'endpoints' not in db_core:
            print('Failed to find endpoints in db_core')
            return False

        endpoints = db_core['endpoints']

        if 'image' not in endpoints:
            print('Failed to find image in endpoints')
            return False

        self.image_base = endpoints['image']

        if 'thumb' not in endpoints:
            print('Failed to find thumb in endpoints')
            return False

        self.thumb_base = endpoints['thumb']

        if 'web' not in endpoints:
            print('Failed to find web in endpoints')
            return False

        return True

    def get_summary(self):
        url = '/v2/core'
        return self.response(url)

    def get_account_direct(self):
        url = '/v2/core/account'
        return self.response(url)

    def get_account(self):
        account_data = self.get_account_direct()
        if account_data and account_data['user']:
            # TODO some actual error checking would be nice :-)
            return digital_blasphemy_account(
                account_data['user']['active'],
                account_data['user']['display_name'],
                account_data['user']['id'],
                account_data['user']['lifetime'],
                account_data['user']['plus'],
            )

    def get_wallpapers_direct(self, page:int=1, limit:int=10, order:str='desc'):
        url = f'/v2/core/wallpapers'
        query_args = {
            'page': page,
            'limit': limit,
            'order': order
        }
        return self.response(url, query_args=query_args)

    def get_wallpaper_direct(self, wallpaper_id:int, width:int, height:int, wallpaper_type:str, show_watermark:bool=True):
        url = f'/v2/core/download/wallpaper/{wallpaper_type}/{width}/{height}/{wallpaper_id}'
        print(f'get_wallpaper - url: {url}')

        return self.response(url, query_args={'show_watermark': show_watermark})

    def download_wallpaper(self, wallpaper_id:int, width:int, height:int, wallpaper_type:str, show_watermark:bool=True, filename:str="file.png") -> bool:
        wallpaper_data = self.get_wallpaper_direct(wallpaper_id, width, height, wallpaper_type, show_watermark)
        if not wallpaper_data:
            print('Failed to get wallpaper data')
            return False

        if 'download' not in wallpaper_data:
            print('Failed to find request in wallpaper data')
            return False

        download_data = wallpaper_data['download']

        if 'url' not in download_data:
            print('Failed to find url in donwload data')
            return False

        url = download_data['url']
        return self.get_file(url, filename)


def dict_to_query_str(d:dict) -> str:
    if not d:
        return ''
    return '&'.join([f'{k}={v}' for k, v in d.items()])

def main(argv):
    print('Starting')
    api_key_env = os.environ.get('DB_API_KEY')
    if api_key_env is None:
        print('API Key not found. Please set the environment variable DB_API_KEY')
        sys.exit(1)
    db = digital_blasphemy(api_key_env)
    if not db.init():
        print('Failed to initialize')
        sys.exit(1)

    # test = db.get_wallpapers_direct(1, 10, 'desc')
    # out_file = open("myfile.json", "w")
    # print(json.dump(test, out_file))

    test = db.get_wallpaper_direct(51889, 1920, 1080, 'single', True)
    print(test)

    test = db.download_wallpaper(51889, 1920, 1080, 'single', True, 'test.jpg')

if __name__ == '__main__':
    main(sys.argv[1:])
