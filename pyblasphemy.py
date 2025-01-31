#!env python3

import os
import sys
import http.client
import argparse
import json



class digital_blasphemy:
    API_BASE = "api.digitalblasphemy.com"
    def __init__(self, api_key:str):
        self.api_key = api_key

    def response(self, url, payload=None, headers=None):
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

        if not url.startswith("/v2/"):
            url = f"/v2{url}"

        conn.request(method, url, payload, headers)
        response = conn.getresponse()
        data = response.read()
        parsed_data = json.loads(data)
        return parsed_data

    def get_summary(self):
        url = "/core"
        return self.response(url)

    def get_account(self):
        url = "/core/account"
        return self.response(url)

def main(argv):
    api_key_env = os.environ.get('DB_API_KEY')
    if api_key_env is None:
        print("API Key not found. Please set the environment variable DB_API_KEY")
        sys.exit(1)
    db = digital_blasphemy(api_key_env)

    test = db.get_account()
    print(test)

if __name__ == "__main__":
    main(sys.argv[1:])