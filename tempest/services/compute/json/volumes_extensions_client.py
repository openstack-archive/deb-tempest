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
from six.moves.urllib import parse as urllib
from tempest_lib import exceptions as lib_exc

from tempest.api_schema.response.compute.v2_1 import volumes as schema
from tempest.common import service_client


class VolumesExtensionsClient(service_client.ServiceClient):

    def list_volumes(self, detail=False, **params):
        """List all the volumes created."""
        url = 'os-volumes'

        if detail:
            url += '/detail'
        if params:
            url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        body = json.loads(body)
        self.validate_response(schema.list_volumes, resp, body)
        return service_client.ResponseBodyList(resp, body['volumes'])

    def show_volume(self, volume_id):
        """Returns the details of a single volume."""
        url = "os-volumes/%s" % volume_id
        resp, body = self.get(url)
        body = json.loads(body)
        self.validate_response(schema.create_get_volume, resp, body)
        return service_client.ResponseBody(resp, body['volume'])

    def create_volume(self, **kwargs):
        """
        Creates a new Volume.
        size(Required): Size of volume in GB.
        Following optional keyword arguments are accepted:
        display_name: Optional Volume Name.
        metadata: A dictionary of values to be used as metadata.
        """
        post_body = json.dumps({'volume': kwargs})
        resp, body = self.post('os-volumes', post_body)
        body = json.loads(body)
        self.validate_response(schema.create_get_volume, resp, body)
        return service_client.ResponseBody(resp, body['volume'])

    def delete_volume(self, volume_id):
        """Deletes the Specified Volume."""
        resp, body = self.delete("os-volumes/%s" % volume_id)
        self.validate_response(schema.delete_volume, resp, body)
        return service_client.ResponseBody(resp, body)

    def is_resource_deleted(self, id):
        try:
            self.show_volume(id)
        except lib_exc.NotFound:
            return True
        return False

    @property
    def resource_type(self):
        """Returns the primary type of resource this client works with."""
        return 'volume'
