# Copyright 2016 NEC Corporation.  All rights reserved.
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

from tempest.lib.services.image.v2 import resource_types_client
from tempest.tests.lib import fake_auth_provider
from tempest.tests.lib.services import base


class TestResouceTypesClient(base.BaseServiceTest):
    FAKE_LIST_RESOURCETYPES = {
        "resource_types": [
            {
                "created_at": "2014-08-28T18:13:04Z",
                "name": "OS::Glance::Image",
                "updated_at": "2014-08-28T18:13:04Z"
            },
            {
                "created_at": "2014-08-28T18:13:04Z",
                "name": "OS::Cinder::Volume",
                "updated_at": "2014-08-28T18:13:04Z"
            },
            {
                "created_at": "2014-08-28T18:13:04Z",
                "name": "OS::Nova::Flavor",
                "updated_at": "2014-08-28T18:13:04Z"
            },
            {
                "created_at": "2014-08-28T18:13:04Z",
                "name": "OS::Nova::Aggregate",
                "updated_at": "2014-08-28T18:13:04Z"
            },
            {
                "created_at": "2014-08-28T18:13:04Z",
                "name": u"\u2740(*\xb4\u25e1`*)\u2740",
                "updated_at": "2014-08-28T18:13:04Z"
            }
        ]
    }

    def setUp(self):
        super(TestResouceTypesClient, self).setUp()
        fake_auth = fake_auth_provider.FakeAuthProvider()
        self.client = resource_types_client.ResourceTypesClient(fake_auth,
                                                                'image',
                                                                'regionOne')

    def _test_list_resouce_types(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_resource_types,
            'tempest.lib.common.rest_client.RestClient.get',
            self.FAKE_LIST_RESOURCETYPES,
            bytes_body)

    def test_list_resouce_types_with_str_body(self):
        self._test_list_resouce_types()

    def test_list_resouce_types_with_bytes_body(self):
        self._test_list_resouce_types(bytes_body=True)
