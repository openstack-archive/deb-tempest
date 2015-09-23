# Copyright 2013 NEC Corporation
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

from oslo_log import log as logging

from tempest.common import custom_matchers
from tempest.common import waiters
from tempest import config
from tempest import exceptions
from tempest.scenario import manager
from tempest import test

CONF = config.CONF

LOG = logging.getLogger(__name__)


class TestMinimumBasicScenario(manager.ScenarioTest):

    """
    This is a basic minimum scenario test.

    This test below:
    * across the multiple components
    * as a regular user
    * with and without optional parameters
    * check command outputs

    """

    def _wait_for_server_status(self, status):
        server_id = self.server['id']
        # Raise on error defaults to True, which is consistent with the
        # original function from scenario tests here
        waiters.wait_for_server_status(self.servers_client,
                                       server_id, status)

    def nova_keypair_add(self):
        self.keypair = self.create_keypair()

    def nova_boot(self):
        create_kwargs = {'key_name': self.keypair['name']}
        self.server = self.create_server(image=self.image,
                                         create_kwargs=create_kwargs)

    def nova_list(self):
        servers = self.servers_client.list_servers()
        # The list servers in the compute client is inconsistent...
        servers = servers['servers']
        self.assertIn(self.server['id'], [x['id'] for x in servers])

    def nova_show(self):
        got_server = self.servers_client.show_server(self.server['id'])
        excluded_keys = ['OS-EXT-AZ:availability_zone']
        # Exclude these keys because of LP:#1486475
        excluded_keys.extend(['OS-EXT-STS:power_state', 'updated'])
        self.assertThat(
            self.server, custom_matchers.MatchesDictExceptForKeys(
                got_server, excluded_keys=excluded_keys))

    def cinder_create(self):
        self.volume = self.create_volume()

    def cinder_list(self):
        volumes = self.volumes_client.list_volumes()['volumes']
        self.assertIn(self.volume['id'], [x['id'] for x in volumes])

    def cinder_show(self):
        volume = self.volumes_client.show_volume(self.volume['id'])['volume']
        self.assertEqual(self.volume, volume)

    def nova_reboot(self):
        self.servers_client.reboot_server(self.server['id'], 'SOFT')
        self._wait_for_server_status('ACTIVE')

    def check_partitions(self):
        # NOTE(andreaf) The device name may be different on different guest OS
        partitions = self.linux_client.get_partitions()
        self.assertEqual(1, partitions.count(CONF.compute.volume_device_name))

    def create_and_add_security_group(self):
        secgroup = self._create_security_group()
        self.servers_client.add_security_group(self.server['id'],
                                               secgroup['name'])
        self.addCleanup(self.servers_client.remove_security_group,
                        self.server['id'], secgroup['name'])

        def wait_for_secgroup_add():
            body = self.servers_client.show_server(self.server['id'])
            return {'name': secgroup['name']} in body['security_groups']

        if not test.call_until_true(wait_for_secgroup_add,
                                    CONF.compute.build_timeout,
                                    CONF.compute.build_interval):
            msg = ('Timed out waiting for adding security group %s to server '
                   '%s' % (secgroup['id'], self.server['id']))
            raise exceptions.TimeoutException(msg)

    @test.idempotent_id('bdbb5441-9204-419d-a225-b4fdbfb1a1a8')
    @test.services('compute', 'volume', 'image', 'network')
    def test_minimum_basic_scenario(self):
        self.glance_image_create()
        self.nova_keypair_add()
        self.nova_boot()
        self.nova_list()
        self.nova_show()
        self.cinder_create()
        self.cinder_list()
        self.cinder_show()
        self.nova_volume_attach()
        self.addCleanup(self.nova_volume_detach)
        self.cinder_show()

        self.floating_ip = self.create_floating_ip(self.server)
        self.create_and_add_security_group()

        self.linux_client = self.get_remote_client(self.floating_ip['ip'])
        self.nova_reboot()

        self.linux_client = self.get_remote_client(self.floating_ip['ip'])
        self.check_partitions()
