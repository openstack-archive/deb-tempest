# Copyright 2013 OpenStack Foundation
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

import six

from tempest.api.network import base
from tempest.common.utils import data_utils
from tempest.lib import exceptions as lib_exc
from tempest import test


class QuotasTest(base.BaseAdminNetworkTest):
    """Tests the following operations in the Neutron API:

        list quotas for tenants who have non-default quota values
        show quotas for a specified tenant
        update quotas for a specified tenant
        reset quotas to default values for a specified tenant

    v2.0 of the API is assumed.
    It is also assumed that the per-tenant quota extension API is configured
    in /etc/neutron/neutron.conf as follows:

        quota_driver = neutron.db.quota_db.DbQuotaDriver
    """

    @classmethod
    def skip_checks(cls):
        super(QuotasTest, cls).skip_checks()
        if not test.is_extension_enabled('quotas', 'network'):
            msg = "quotas extension not enabled."
            raise cls.skipException(msg)

    @classmethod
    def setup_clients(cls):
        super(QuotasTest, cls).setup_clients()
        cls.identity_admin_client = cls.os_adm.identity_client

    def _check_quotas(self, new_quotas):
        # Add a tenant to conduct the test
        project = data_utils.rand_name('test_project_')
        description = data_utils.rand_name('desc_')
        project = self.identity_utils.create_project(name=project,
                                                     description=description)
        project_id = project['id']
        self.addCleanup(self.identity_utils.delete_project, project_id)

        # Change quotas for tenant
        quota_set = self.admin_quotas_client.update_quotas(
            project_id, **new_quotas)['quota']
        self.addCleanup(self._cleanup_quotas, project_id)
        for key, value in six.iteritems(new_quotas):
            self.assertEqual(value, quota_set[key])

        # Confirm our tenant is listed among tenants with non default quotas
        non_default_quotas = self.admin_quotas_client.list_quotas()
        found = False
        for qs in non_default_quotas['quotas']:
            if qs['tenant_id'] == project_id:
                found = True
        self.assertTrue(found)

        # Confirm from API quotas were changed as requested for tenant
        quota_set = self.admin_quotas_client.show_quotas(project_id)
        quota_set = quota_set['quota']
        for key, value in six.iteritems(new_quotas):
            self.assertEqual(value, quota_set[key])

        # Reset quotas to default and confirm
        self.admin_quotas_client.reset_quotas(project_id)
        non_default_quotas = self.admin_quotas_client.list_quotas()
        for q in non_default_quotas['quotas']:
            self.assertNotEqual(project_id, q['tenant_id'])

    @test.idempotent_id('2390f766-836d-40ef-9aeb-e810d78207fb')
    def test_quotas(self):
        new_quotas = {'network': 0, 'security_group': 0}
        self._check_quotas(new_quotas)

    def _cleanup_quotas(self, project_id):
        # try to clean up the resources.If it fails, then
        # assume that everything was already deleted, so
        # it is OK to continue.
        try:
            self.admin_quotas_client.reset_quotas(project_id)
        except lib_exc.NotFound:
            pass
