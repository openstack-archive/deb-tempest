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

from tempest.api.compute import base
from tempest import test


class InstanceActionsV3Test(base.BaseV3ComputeTest):

    @classmethod
    def resource_setup(cls):
        super(InstanceActionsV3Test, cls).resource_setup()
        cls.client = cls.servers_client
        resp, server = cls.create_test_server(wait_until='ACTIVE')
        cls.resp = resp
        cls.server_id = server['id']

    @test.attr(type='gate')
    def test_list_server_actions(self):
        # List actions of the provided server
        resp, body = self.client.reboot(self.server_id, 'HARD')
        self.client.wait_for_server_status(self.server_id, 'ACTIVE')

        resp, body = self.client.list_server_actions(self.server_id)
        self.assertEqual(200, resp.status)
        self.assertTrue(len(body) == 2, str(body))
        self.assertTrue(any([i for i in body if i['action'] == 'create']))
        self.assertTrue(any([i for i in body if i['action'] == 'reboot']))

    @test.attr(type='gate')
    def test_get_server_action(self):
        # Get the action details of the provided server
        request_id = self.resp['x-openstack-request-id']
        resp, body = self.client.get_server_action(self.server_id,
                                                   request_id)
        self.assertEqual(200, resp.status)
        self.assertEqual(self.server_id, body['server_uuid'])
        self.assertEqual('create', body['action'])
