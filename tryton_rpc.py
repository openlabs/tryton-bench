# -*- coding: utf-8 -*-
"""
    tryton_rpc

    Easy to use JSON RPC client for Tryton based on pyjsonrpc

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: Modified BSD, see LICENSE for more details.
"""


import requests
import json


#FIXME: kwargs not working


class HttpClient:
    def __init__(self, url, database_name, user, passwd):
        self._url = '{}/{}'.format(url, database_name)
        self._user = user
        self._passwd = passwd
        self._login()

    def _login(self):
        payload = json.dumps({
            'params': [self._user, self._passwd],
            'jsonrpc': "2.0",
            'method': 'common.login',
            'id': None
        })
        result = requests.post(self._url, payload)
        self._session = json.loads(result.text)['result']
        return self._session

    def call(self, model, method, *args, **kwargs):
        method = '{}.{}.{}'.format('model', model, method)
        payload = json.dumps({
            'params': [
                self._session[0],
                self._session[1],
            ] + list(args) + [kwargs],
            'method': method,
            'id': None
        })
        return requests.post(self._url, payload).status_code


if __name__ == "__main__":
    c = HttpClient("http://localhost:8000", "tryton_rpc", "admin", "12345")
    #c.call('hello.hello', 'create',
            #[{'name': "Vishsh2", "greeting": "Sup?"}])
    #c.call('hello.hello', 'create',
            #vlist=[{'name': "Vishsh2", "greeting": "Sup?"}])
