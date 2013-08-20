# -*- coding: utf-8 -*-
"""
    hello

    Scenario for Hello World module

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: Modified BSD, see LICENSE for more details.
"""

import uuid


MODEL = 'hello.hello'
METHOD = 'create'


"""
def generate():
    return {
        'kwargs': {
            'vlist': [{
                'name': str(uuid.uuid1()),
                'greeting': str(uuid.uuid1()),
            }],
        },
    }
"""


def generate():
    return {
        'args': [
            [{
                'name': str(uuid.uuid1()),
                'greeting': str(uuid.uuid1()),
            }],
        ],
    }
