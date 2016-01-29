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

import httplib2
import mock
from tempest_lib.common import rest_client

from tempest.services.compute.json import base as base_compute_client
from tempest.tests import fake_auth_provider
from tempest.tests.services.compute import base


class TestClientWithoutMicroversionHeader(base.BaseComputeServiceTest):

    def setUp(self):
        super(TestClientWithoutMicroversionHeader, self).setUp()
        fake_auth = fake_auth_provider.FakeAuthProvider()
        self.client = base_compute_client.BaseComputeClient(
            fake_auth, 'compute', 'regionOne')

    def test_no_microverion_header(self):
        header = self.client.get_headers()
        self.assertNotIn('X-OpenStack-Nova-API-Version', header)

    def test_no_microverion_header_in_raw_request(self):
        def raw_request(*args, **kwargs):
            self.assertNotIn('X-OpenStack-Nova-API-Version', kwargs['headers'])
            return (httplib2.Response({'status': 200}), {})

        with mock.patch.object(rest_client.RestClient,
                               'raw_request') as mock_get:
            mock_get.side_effect = raw_request
            self.client.get('fake_url')


class TestClientWithMicroversionHeader(base.BaseComputeServiceTest):

    def setUp(self):
        super(TestClientWithMicroversionHeader, self).setUp()
        fake_auth = fake_auth_provider.FakeAuthProvider()
        self.client = base_compute_client.BaseComputeClient(
            fake_auth, 'compute', 'regionOne')
        self.client.api_microversion = '2.2'

    def test_microverion_header(self):
        header = self.client.get_headers()
        self.assertIn('X-OpenStack-Nova-API-Version', header)
        self.assertEqual(self.client.api_microversion,
                         header['X-OpenStack-Nova-API-Version'])

    def test_microverion_header_in_raw_request(self):
        def raw_request(*args, **kwargs):
            self.assertIn('X-OpenStack-Nova-API-Version', kwargs['headers'])
            self.assertEqual(self.client.api_microversion,
                             kwargs['headers']['X-OpenStack-Nova-API-Version'])
            return (httplib2.Response({'status': 200}), {})

        with mock.patch.object(rest_client.RestClient,
                               'raw_request') as mock_get:
            mock_get.side_effect = raw_request
            self.client.get('fake_url')
