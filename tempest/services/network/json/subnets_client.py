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

from tempest.services.network.json import base


class SubnetsClient(base.BaseNetworkClient):

    def create_subnet(self, **kwargs):
        uri = '/subnets'
        post_data = {'subnet': kwargs}
        return self.create_resource(uri, post_data)

    def update_subnet(self, subnet_id, **kwargs):
        uri = '/subnets/%s' % subnet_id
        post_data = {'subnet': kwargs}
        return self.update_resource(uri, post_data)

    def show_subnet(self, subnet_id, **fields):
        uri = '/subnets/%s' % subnet_id
        return self.show_resource(uri, **fields)

    def delete_subnet(self, subnet_id):
        uri = '/subnets/%s' % subnet_id
        return self.delete_resource(uri)

    def list_subnets(self, **filters):
        uri = '/subnets'
        return self.list_resources(uri, **filters)
