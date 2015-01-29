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

import StringIO

from tempest.api.compute import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import test

CONF = config.CONF


class ImagesMetadataTestJSON(base.BaseV2ComputeTest):

    @classmethod
    def resource_setup(cls):
        super(ImagesMetadataTestJSON, cls).resource_setup()
        if not CONF.service_available.glance:
            skip_msg = ("%s skipped as glance is not available" % cls.__name__)
            raise cls.skipException(skip_msg)

        cls.glance_client = cls.os.image_client
        cls.client = cls.images_client
        cls.image_id = None

        name = data_utils.rand_name('image')
        resp, body = cls.glance_client.create_image(name=name,
                                                    container_format='bare',
                                                    disk_format='raw',
                                                    is_public=False)
        cls.image_id = body['id']
        cls.images.append(cls.image_id)
        image_file = StringIO.StringIO(('*' * 1024))
        cls.glance_client.update_image(cls.image_id, data=image_file)
        cls.client.wait_for_image_status(cls.image_id, 'ACTIVE')

    def setUp(self):
        super(ImagesMetadataTestJSON, self).setUp()
        meta = {'key1': 'value1', 'key2': 'value2'}
        resp, _ = self.client.set_image_metadata(self.image_id, meta)
        self.assertEqual(resp.status, 200)

    @test.attr(type='gate')
    def test_list_image_metadata(self):
        # All metadata key/value pairs for an image should be returned
        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)

    @test.attr(type='gate')
    def test_set_image_metadata(self):
        # The metadata for the image should match the new values
        req_metadata = {'meta2': 'value2', 'meta3': 'value3'}
        resp, body = self.client.set_image_metadata(self.image_id,
                                                    req_metadata)

        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        self.assertEqual(req_metadata, resp_metadata)

    @test.attr(type='gate')
    def test_update_image_metadata(self):
        # The metadata for the image should match the updated values
        req_metadata = {'key1': 'alt1', 'key3': 'value3'}
        resp, metadata = self.client.update_image_metadata(self.image_id,
                                                           req_metadata)

        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key1': 'alt1', 'key2': 'value2', 'key3': 'value3'}
        self.assertEqual(expected, resp_metadata)

    @test.attr(type='gate')
    def test_get_image_metadata_item(self):
        # The value for a specific metadata key should be returned
        resp, meta = self.client.get_image_metadata_item(self.image_id,
                                                         'key2')
        self.assertEqual('value2', meta['key2'])

    @test.attr(type='gate')
    def test_set_image_metadata_item(self):
        # The value provided for the given meta item should be set for
        # the image
        meta = {'key1': 'alt'}
        resp, body = self.client.set_image_metadata_item(self.image_id,
                                                         'key1', meta)
        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key1': 'alt', 'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)

    @test.attr(type='gate')
    def test_delete_image_metadata_item(self):
        # The metadata value/key pair should be deleted from the image
        resp, body = self.client.delete_image_metadata_item(self.image_id,
                                                            'key1')
        resp, resp_metadata = self.client.list_image_metadata(self.image_id)
        expected = {'key2': 'value2'}
        self.assertEqual(expected, resp_metadata)


class ImagesMetadataTestXML(ImagesMetadataTestJSON):
    _interface = 'xml'
