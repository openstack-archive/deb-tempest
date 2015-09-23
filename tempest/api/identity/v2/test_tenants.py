# Copyright 2015 OpenStack Foundation
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

from tempest_lib import exceptions as lib_exc

from tempest.api.identity import base
from tempest import test


class IdentityTenantsTest(base.BaseIdentityV2Test):

    credentials = ['primary', 'alt']

    @test.idempotent_id('ecae2459-243d-4ba1-ad02-65f15dc82b78')
    def test_list_tenants_returns_only_authorized_tenants(self):
        alt_tenant_name = self.alt_manager.credentials.credentials.tenant_name
        resp = self.non_admin_client.list_tenants()

        # check that user can see only that tenants that he presents in so user
        # can successfully authenticate using his credentials and tenant name
        # from received tenants list
        for tenant in resp['tenants']:
            body = self.non_admin_token_client.auth(
                self.os.credentials.username,
                self.os.credentials.password,
                tenant['name'])
            self.assertNotEmpty(body['token']['id'])
            self.assertEqual(body['token']['tenant']['id'], tenant['id'])
            self.assertEqual(body['token']['tenant']['name'], tenant['name'])
            self.assertEqual(body['user']['id'], self.os.credentials.user_id)

        # check that user cannot log in to alt user's tenant
        self.assertRaises(
            lib_exc.Unauthorized,
            self.non_admin_token_client.auth,
            self.os.credentials.username,
            self.os.credentials.password,
            alt_tenant_name)
