# Copyright 2016 NEC Corporation.  All rights reserved.
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

import copy

from tempest.lib.api_schema.response.compute.v2_1 import servers

get_server = copy.deepcopy(servers.get_server)
get_server['response_body']['properties']['server'][
    'properties'].update({'locked': {'type': 'boolean'}})
get_server['response_body']['properties']['server'][
    'required'].append('locked')

list_servers_detail = copy.deepcopy(servers.list_servers_detail)
list_servers_detail['response_body']['properties']['servers']['items'][
    'properties'].update({'locked': {'type': 'boolean'}})
list_servers_detail['response_body']['properties']['servers']['items'][
    'required'].append('locked')
