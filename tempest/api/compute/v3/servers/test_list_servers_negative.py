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

import datetime

from six import moves

from tempest.api.compute import base
from tempest import exceptions
from tempest import test


class ListServersNegativeV3Test(base.BaseV3ComputeTest):
    force_tenant_isolation = True

    @classmethod
    def resource_setup(cls):
        super(ListServersNegativeV3Test, cls).resource_setup()
        cls.client = cls.servers_client

        # The following servers are created for use
        # by the test methods in this class. These
        # servers are cleaned up automatically in the
        # tearDownClass method of the super-class.
        cls.existing_fixtures = []
        cls.deleted_fixtures = []
        cls.start_time = datetime.datetime.utcnow()
        for x in moves.xrange(2):
            resp, srv = cls.create_test_server(wait_until='ACTIVE')
            cls.existing_fixtures.append(srv)

        resp, srv = cls.create_test_server()
        cls.client.delete_server(srv['id'])
        # We ignore errors on termination because the server may
        # be put into ERROR status on a quick spawn, then delete,
        # as the compute node expects the instance local status
        # to be spawning, not deleted. See LP Bug#1061167
        cls.client.wait_for_server_termination(srv['id'],
                                               ignore_error=True)
        cls.deleted_fixtures.append(srv)

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_with_a_deleted_server(self):
        # Verify deleted servers do not show by default in list servers
        # List servers and verify server not returned
        resp, body = self.client.list_servers()
        servers = body['servers']
        deleted_ids = [s['id'] for s in self.deleted_fixtures]
        actual = [srv for srv in servers
                  if srv['id'] in deleted_ids]
        self.assertEqual('200', resp['status'])
        self.assertEqual([], actual)

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_non_existing_image(self):
        # Listing servers for a non existing image returns empty list
        non_existing_image = '1234abcd-zzz0-aaa9-ppp3-0987654abcde'
        resp, body = self.client.list_servers(dict(image=non_existing_image))
        servers = body['servers']
        self.assertEqual('200', resp['status'])
        self.assertEqual([], servers)

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_non_existing_flavor(self):
        # Listing servers by non existing flavor returns empty list
        non_existing_flavor = 1234
        resp, body = self.client.list_servers(dict(flavor=non_existing_flavor))
        servers = body['servers']
        self.assertEqual('200', resp['status'])
        self.assertEqual([], servers)

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_non_existing_server_name(self):
        # Listing servers for a non existent server name returns empty list
        non_existing_name = 'junk_server_1234'
        resp, body = self.client.list_servers(dict(name=non_existing_name))
        servers = body['servers']
        self.assertEqual('200', resp['status'])
        self.assertEqual([], servers)

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_status_non_existing(self):
        # Return an empty list when invalid status is specified
        non_existing_status = 'BALONEY'
        resp, body = self.client.list_servers(dict(status=non_existing_status))
        servers = body['servers']
        self.assertEqual('200', resp['status'])
        self.assertEqual([], servers)

    @test.attr(type='gate')
    def test_list_servers_by_limits(self):
        # List servers by specifying limits
        resp, body = self.client.list_servers({'limit': 1})
        self.assertEqual('200', resp['status'])
        self.assertEqual(1, len([x for x in body['servers'] if 'id' in x]))

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_limits_greater_than_actual_count(self):
        # List servers by specifying a greater value for limit
        resp, body = self.client.list_servers({'limit': 100})
        self.assertEqual('200', resp['status'])
        self.assertEqual(len(self.existing_fixtures), len(body['servers']))

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_limits_pass_string(self):
        # Return an error if a string value is passed for limit
        self.assertRaises(exceptions.BadRequest, self.client.list_servers,
                          {'limit': 'testing'})

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_limits_pass_negative_value(self):
        # Return an error if a negative value for limit is passed
        self.assertRaises(exceptions.BadRequest, self.client.list_servers,
                          {'limit': -1})

    @test.attr(type='gate')
    def test_list_servers_by_changes_since(self):
        # Servers are listed by specifying changes-since date
        changes_since = {'changes_since': self.start_time.isoformat()}
        resp, body = self.client.list_servers(changes_since)
        self.assertEqual('200', resp['status'])
        # changes-since returns all instances, including deleted.
        num_expected = (len(self.existing_fixtures) +
                        len(self.deleted_fixtures))
        self.assertEqual(num_expected, len(body['servers']),
                         "Number of servers %d is wrong in %s" %
                         (num_expected, body['servers']))

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_changes_since_invalid_date(self):
        # Return an error when invalid date format is passed
        self.assertRaises(exceptions.BadRequest, self.client.list_servers,
                          {'changes_since': '2011/01/01'})

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_by_changes_since_future_date(self):
        # Return an empty list when a date in the future is passed
        changes_since = {'changes_since': '2051-01-01T12:34:00Z'}
        resp, body = self.client.list_servers(changes_since)
        self.assertEqual('200', resp['status'])
        self.assertEqual(0, len(body['servers']))

    @test.attr(type=['negative', 'gate'])
    def test_list_servers_detail_server_is_deleted(self):
        # Server details are not listed for a deleted server
        deleted_ids = [s['id'] for s in self.deleted_fixtures]
        resp, body = self.client.list_servers_with_detail()
        servers = body['servers']
        actual = [srv for srv in servers
                  if srv['id'] in deleted_ids]
        self.assertEqual('200', resp['status'])
        self.assertEqual([], actual)
