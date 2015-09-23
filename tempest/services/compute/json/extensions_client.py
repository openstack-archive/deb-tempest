# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
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

from oslo_serialization import jsonutils as json

from tempest.api_schema.response.compute.v2_1 import extensions as schema
from tempest.common import service_client


class ExtensionsClient(service_client.ServiceClient):

    def list_extensions(self):
        url = 'extensions'
        resp, body = self.get(url)
        body = json.loads(body)
        self.validate_response(schema.list_extensions, resp, body)
        return service_client.ResponseBody(resp, body)

    def show_extension(self, extension_alias):
        resp, body = self.get('extensions/%s' % extension_alias)
        body = json.loads(body)
        return service_client.ResponseBody(resp, body)
