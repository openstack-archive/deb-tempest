# Copyright 2012 IBM Corp.
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

import time
import urllib

from lxml import etree

from tempest.common import rest_client
from tempest.common import xml_utils
from tempest import config
from tempest import exceptions

CONF = config.CONF


class VolumesExtensionsClientXML(rest_client.RestClient):
    TYPE = "xml"

    def __init__(self, auth_provider):
        super(VolumesExtensionsClientXML, self).__init__(
            auth_provider)
        self.service = CONF.compute.catalog_type
        self.build_interval = CONF.compute.build_interval
        self.build_timeout = CONF.compute.build_timeout

    def _parse_volume(self, body):
        vol = dict((attr, body.get(attr)) for attr in body.keys())

        for child in body.getchildren():
            tag = child.tag
            if tag.startswith("{"):
                ns, tag = tag.split("}", 1)
            if tag == 'metadata':
                vol['metadata'] = dict((meta.get('key'),
                                        meta.text) for meta in list(child))
            else:
                vol[tag] = xml_utils.xml_to_json(child)
        return vol

    def list_volumes(self, params=None):
        """List all the volumes created."""
        url = 'os-volumes'

        if params:
            url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        body = etree.fromstring(body)
        volumes = []
        if body is not None:
            volumes += [self._parse_volume(vol) for vol in list(body)]
        return resp, volumes

    def list_volumes_with_detail(self, params=None):
        """List all the details of volumes."""
        url = 'os-volumes/detail'

        if params:
            url += '?%s' % urllib.urlencode(params)

        resp, body = self.get(url)
        body = etree.fromstring(body)
        volumes = []
        if body is not None:
            volumes += [self._parse_volume(vol) for vol in list(body)]
        return resp, volumes

    def get_volume(self, volume_id):
        """Returns the details of a single volume."""
        url = "os-volumes/%s" % str(volume_id)
        resp, body = self.get(url)
        body = etree.fromstring(body)
        return resp, self._parse_volume(body)

    def create_volume(self, size, display_name=None, metadata=None):
        """Creates a new Volume.

        :param size: Size of volume in GB. (Required)
        :param display_name: Optional Volume Name.
        :param metadata: An optional dictionary of values for metadata.
        """
        volume = xml_utils.Element("volume",
                                   xmlns=xml_utils.XMLNS_11,
                                   size=size)
        if display_name:
            volume.add_attr('display_name', display_name)

        if metadata:
            _metadata = xml_utils.Element('metadata')
            volume.append(_metadata)
            for key, value in metadata.items():
                meta = xml_utils.Element('meta')
                meta.add_attr('key', key)
                meta.append(xml_utils.Text(value))
                _metadata.append(meta)

        resp, body = self.post('os-volumes', str(xml_utils.Document(volume)))
        body = xml_utils.xml_to_json(etree.fromstring(body))
        return resp, body

    def delete_volume(self, volume_id):
        """Deletes the Specified Volume."""
        return self.delete("os-volumes/%s" % str(volume_id))

    def wait_for_volume_status(self, volume_id, status):
        """Waits for a Volume to reach a given status."""
        resp, body = self.get_volume(volume_id)
        volume_name = body['displayName']
        volume_status = body['status']
        start = int(time.time())

        while volume_status != status:
            time.sleep(self.build_interval)
            resp, body = self.get_volume(volume_id)
            volume_status = body['status']
            if volume_status == 'error':
                raise exceptions.VolumeBuildErrorException(volume_id=volume_id)

            if int(time.time()) - start >= self.build_timeout:
                message = 'Volume %s failed to reach %s status within '\
                          'the required time (%s s).' % (volume_name, status,
                                                         self.build_timeout)
                raise exceptions.TimeoutException(message)

    def is_resource_deleted(self, id):
        try:
            self.get_volume(id)
        except exceptions.NotFound:
            return True
        return False

    @property
    def resource_type(self):
        """Returns the primary type of resource this client works with."""
        return 'volume'
