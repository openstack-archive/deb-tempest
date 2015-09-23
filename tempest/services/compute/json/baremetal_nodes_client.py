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

from oslo_serialization import jsonutils as json
from six.moves.urllib import parse as urllib

from tempest.api_schema.response.compute.v2_1 import baremetal_nodes \
    as schema
from tempest.common import service_client


class BaremetalNodesClient(service_client.ServiceClient):
    """
    Tests Baremetal API
    """

    def list_baremetal_nodes(self, **params):
        """List all baremetal nodes."""
        url = 'os-baremetal-nodes'
        if params:
            url += '?%s' % urllib.urlencode(params)
        resp, body = self.get(url)
        body = json.loads(body)
        self.validate_response(schema.list_baremetal_nodes, resp, body)
        return service_client.ResponseBody(resp, body)

    def show_baremetal_node(self, baremetal_node_id):
        """Returns the details of a single baremetal node."""
        url = 'os-baremetal-nodes/%s' % baremetal_node_id
        resp, body = self.get(url)
        body = json.loads(body)
        self.validate_response(schema.get_baremetal_node, resp, body)
        return service_client.ResponseBody(resp, body)
