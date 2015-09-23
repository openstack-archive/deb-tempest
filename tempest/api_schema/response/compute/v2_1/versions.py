# Copyright 2015 NEC Corporation.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

list_versions = {
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'versions': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                        'links': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'href': {'type': 'string',
                                             'format': 'uri'},
                                    'rel': {'type': 'string'},
                                },
                                'required': ['href', 'rel'],
                                'additionalProperties': False
                            }
                        },
                        'status': {'type': 'string'},
                        'updated': {'type': 'string', 'format': 'date-time'},
                        'version': {'type': 'string'},
                        'min_version': {'type': 'string'}
                    },
                    # NOTE: version and min_version have been added since Kilo,
                    # so they should not be required.
                    'required': ['id', 'links', 'status', 'updated'],
                    'additionalProperties': False
                }
            }
        },
        'required': ['versions'],
        'additionalProperties': False
    }
}
