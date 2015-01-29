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


from tempest.api.compute import base
from tempest.common.utils import data_utils
from tempest import config
from tempest.openstack.common import log as logging
from tempest import test

CONF = config.CONF
LOG = logging.getLogger(__name__)


class ImagesOneServerV3Test(base.BaseV3ComputeTest):

    def setUp(self):
        # NOTE(afazekas): Normally we use the same server with all test cases,
        # but if it has an issue, we build a new one
        super(ImagesOneServerV3Test, self).setUp()
        # Check if the server is in a clean state after test
        try:
            self.servers_client.wait_for_server_status(self.server_id,
                                                       'ACTIVE')
        except Exception:
            LOG.exception('server %s timed out to become ACTIVE. rebuilding'
                          % self.server_id)
            # Rebuild server if cannot reach the ACTIVE state
            # Usually it means the server had a serious accident
            self.__class__.server_id = self.rebuild_server(self.server_id)

    def tearDown(self):
        """Terminate test instances created after a test is executed."""
        self.server_check_teardown()
        super(ImagesOneServerV3Test, self).tearDown()

    @classmethod
    def resource_setup(cls):
        super(ImagesOneServerV3Test, cls).resource_setup()
        cls.client = cls.images_client
        if not CONF.service_available.glance:
            skip_msg = ("%s skipped as glance is not available" % cls.__name__)
            raise cls.skipException(skip_msg)

        resp, server = cls.create_test_server(wait_until='ACTIVE')
        cls.server_id = server['id']

    def _get_default_flavor_disk_size(self, flavor_id):
        resp, flavor = self.flavors_client.get_flavor_details(flavor_id)
        return flavor['disk']

    @test.attr(type='smoke')
    def test_create_delete_image(self):

        # Create a new image
        name = data_utils.rand_name('image')
        meta = {'image_type': 'test'}
        resp, body = self.servers_client.create_image(self.server_id,
                                                      name, meta)
        self.assertEqual(202, resp.status)
        image_id = data_utils.parse_image_id(resp['location'])
        self.client.wait_for_image_status(image_id, 'active')

        # Verify the image was created correctly
        resp, image = self.client.get_image_meta(image_id)
        self.assertEqual(name, image['name'])
        self.assertEqual('test', image['properties']['image_type'])

        resp, original_image = self.client.get_image_meta(self.image_ref)

        # Verify minRAM is the same as the original image
        self.assertEqual(image['min_ram'], original_image['min_ram'])

        # Verify minDisk is the same as the original image or the flavor size
        flavor_disk_size = self._get_default_flavor_disk_size(self.flavor_ref)
        self.assertIn(str(image['min_disk']),
                      (str(original_image['min_disk']), str(flavor_disk_size)))

        # Verify the image was deleted correctly
        resp, body = self.client.delete_image(image_id)
        self.assertEqual('200', resp['status'])
        self.client.wait_for_resource_deletion(image_id)

    @test.attr(type=['gate'])
    def test_create_image_specify_multibyte_character_image_name(self):
        # prefix character is:
        # http://www.fileformat.info/info/unicode/char/1F4A9/index.htm
        utf8_name = data_utils.rand_name(u'\xF0\x9F\x92\xA9')
        resp, body = self.servers_client.create_image(self.server_id,
                                                      utf8_name)
        image_id = data_utils.parse_image_id(resp['location'])
        self.addCleanup(self.client.delete_image, image_id)
        self.assertEqual('202', resp['status'])
