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

from oslo_log import log as logging
from tempest_lib import exceptions as lib_exc

from tempest.common import credentials_factory as common_creds
from tempest.common.utils import data_utils
from tempest import config
import tempest.test

CONF = config.CONF
LOG = logging.getLogger(__name__)


class BaseIdentityTest(tempest.test.BaseTestCase):

    @classmethod
    def disable_user(cls, user_name):
        user = cls.get_user_by_name(user_name)
        cls.client.enable_disable_user(user['id'], False)

    @classmethod
    def disable_tenant(cls, tenant_name):
        tenant = cls.get_tenant_by_name(tenant_name)
        cls.tenants_client.update_tenant(tenant['id'], enabled=False)

    @classmethod
    def get_user_by_name(cls, name):
        users = cls.client.list_users()['users']
        user = [u for u in users if u['name'] == name]
        if len(user) > 0:
            return user[0]

    @classmethod
    def get_tenant_by_name(cls, name):
        try:
            tenants = cls.tenants_client.list_tenants()['tenants']
        except AttributeError:
            tenants = cls.client.list_projects()['projects']
        tenant = [t for t in tenants if t['name'] == name]
        if len(tenant) > 0:
            return tenant[0]

    @classmethod
    def get_role_by_name(cls, name):
        roles = cls.roles_client.list_roles()['roles']
        role = [r for r in roles if r['name'] == name]
        if len(role) > 0:
            return role[0]


class BaseIdentityV2Test(BaseIdentityTest):

    credentials = ['primary']

    # identity v2 tests should obtain tokens and create accounts via v2
    # regardless of the configured CONF.identity.auth_version
    identity_version = 'v2'

    @classmethod
    def setup_clients(cls):
        super(BaseIdentityV2Test, cls).setup_clients()
        cls.non_admin_client = cls.os.identity_public_client
        cls.non_admin_token_client = cls.os.token_client
        cls.non_admin_tenants_client = cls.os.tenants_public_client
        cls.non_admin_roles_client = cls.os.roles_public_client

    @classmethod
    def resource_setup(cls):
        super(BaseIdentityV2Test, cls).resource_setup()

    @classmethod
    def resource_cleanup(cls):
        super(BaseIdentityV2Test, cls).resource_cleanup()


class BaseIdentityV2AdminTest(BaseIdentityV2Test):

    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(BaseIdentityV2AdminTest, cls).setup_clients()
        cls.client = cls.os_adm.identity_client
        cls.non_admin_client = cls.os.identity_client
        cls.token_client = cls.os_adm.token_client
        cls.tenants_client = cls.os_adm.tenants_client
        cls.non_admin_tenants_client = cls.os.tenants_client
        cls.roles_client = cls.os_adm.roles_client
        cls.non_admin_roles_client = cls.os.roles_client

    @classmethod
    def resource_setup(cls):
        super(BaseIdentityV2AdminTest, cls).resource_setup()
        cls.data = DataGenerator(cls.client, cls.tenants_client,
                                 cls.roles_client)

    @classmethod
    def resource_cleanup(cls):
        cls.data.teardown_all()
        super(BaseIdentityV2AdminTest, cls).resource_cleanup()


class BaseIdentityV3Test(BaseIdentityTest):

    credentials = ['primary']

    # identity v3 tests should obtain tokens and create accounts via v3
    # regardless of the configured CONF.identity.auth_version
    identity_version = 'v3'

    @classmethod
    def setup_clients(cls):
        super(BaseIdentityV3Test, cls).setup_clients()
        cls.non_admin_client = cls.os.identity_v3_client
        cls.non_admin_token = cls.os.token_v3_client

    @classmethod
    def resource_cleanup(cls):
        super(BaseIdentityV3Test, cls).resource_cleanup()


class BaseIdentityV3AdminTest(BaseIdentityV3Test):

    credentials = ['primary', 'admin']

    @classmethod
    def setup_clients(cls):
        super(BaseIdentityV3AdminTest, cls).setup_clients()
        cls.client = cls.os_adm.identity_v3_client
        cls.token = cls.os_adm.token_v3_client
        cls.endpoints_client = cls.os_adm.endpoints_client
        cls.region_client = cls.os_adm.region_client
        cls.service_client = cls.os_adm.service_client
        cls.policy_client = cls.os_adm.policy_client
        cls.creds_client = cls.os_adm.credentials_client
        cls.groups_client = cls.os_adm.groups_client

        cls.data = DataGenerator(cls.client)

    @classmethod
    def resource_cleanup(cls):
        cls.data.teardown_all()
        super(BaseIdentityV3AdminTest, cls).resource_cleanup()

    @classmethod
    def get_user_by_name(cls, name):
        users = cls.client.list_users()['users']
        user = [u for u in users if u['name'] == name]
        if len(user) > 0:
            return user[0]

    @classmethod
    def get_tenant_by_name(cls, name):
        tenants = cls.client.list_projects()['projects']
        tenant = [t for t in tenants if t['name'] == name]
        if len(tenant) > 0:
            return tenant[0]

    @classmethod
    def get_role_by_name(cls, name):
        roles = cls.client.list_roles()['roles']
        role = [r for r in roles if r['name'] == name]
        if len(role) > 0:
            return role[0]

    @classmethod
    def disable_user(cls, user_name):
        user = cls.get_user_by_name(user_name)
        cls.client.update_user(user['id'], user_name, enabled=False)

    def delete_domain(self, domain_id):
        # NOTE(mpavlase) It is necessary to disable the domain before deleting
        # otherwise it raises Forbidden exception
        self.client.update_domain(domain_id, enabled=False)
        self.client.delete_domain(domain_id)


class DataGenerator(object):

        def __init__(self, client, tenants_client=None, roles_client=None):
            self.client = client
            # TODO(dmellado) split Datagenerator for v2 and v3
            self.tenants_client = tenants_client
            self.roles_client = roles_client
            self.users = []
            self.tenants = []
            self.roles = []
            self.role_name = None
            self.v3_users = []
            self.projects = []
            self.v3_roles = []
            self.domains = []

        @property
        def test_credentials(self):
            return common_creds.get_credentials(username=self.test_user,
                                                user_id=self.user['id'],
                                                password=self.test_password,
                                                tenant_name=self.test_tenant,
                                                tenant_id=self.tenant['id'])

        def setup_test_user(self):
            """Set up a test user."""
            self.setup_test_tenant()
            self.test_user = data_utils.rand_name('test_user')
            self.test_password = data_utils.rand_password()
            self.test_email = self.test_user + '@testmail.tm'
            self.user = self.client.create_user(self.test_user,
                                                self.test_password,
                                                self.tenant['id'],
                                                self.test_email)['user']
            self.users.append(self.user)

        def setup_test_tenant(self):
            """Set up a test tenant."""
            self.test_tenant = data_utils.rand_name('test_tenant')
            self.test_description = data_utils.rand_name('desc')
            self.tenant = self.tenants_client.create_tenant(
                name=self.test_tenant,
                description=self.test_description)['tenant']
            self.tenants.append(self.tenant)

        def setup_test_role(self):
            """Set up a test role."""
            self.test_role = data_utils.rand_name('role')
            self.role = self.roles_client.create_role(self.test_role)['role']
            self.roles.append(self.role)

        def setup_test_v3_user(self):
            """Set up a test v3 user."""
            self.setup_test_project()
            self.test_user = data_utils.rand_name('test_user')
            self.test_password = data_utils.rand_password()
            self.test_email = self.test_user + '@testmail.tm'
            self.v3_user = self.client.create_user(
                self.test_user,
                password=self.test_password,
                project_id=self.project['id'],
                email=self.test_email)['user']
            self.v3_users.append(self.v3_user)

        def setup_test_project(self):
            """Set up a test project."""
            self.test_project = data_utils.rand_name('test_project')
            self.test_description = data_utils.rand_name('desc')
            self.project = self.client.create_project(
                name=self.test_project,
                description=self.test_description)['project']
            self.projects.append(self.project)

        def setup_test_v3_role(self):
            """Set up a test v3 role."""
            self.test_role = data_utils.rand_name('role')
            self.v3_role = self.client.create_role(self.test_role)['role']
            self.v3_roles.append(self.v3_role)

        def setup_test_domain(self):
            """Set up a test domain."""
            self.test_domain = data_utils.rand_name('test_domain')
            self.test_description = data_utils.rand_name('desc')
            self.domain = self.client.create_domain(
                name=self.test_domain,
                description=self.test_description)['domain']
            self.domains.append(self.domain)

        @staticmethod
        def _try_wrapper(func, item, **kwargs):
            try:
                if kwargs:
                    func(item['id'], **kwargs)
                else:
                    func(item['id'])
            except lib_exc.NotFound:
                pass
            except Exception:
                LOG.exception("Unexpected exception occurred in %s deletion."
                              " But ignored here." % item['id'])

        def teardown_all(self):
            # NOTE(masayukig): v3 client doesn't have v2 method.
            # (e.g. delete_tenant) So we need to check resources existence
            # before using client methods.
            for user in self.users:
                self._try_wrapper(self.client.delete_user, user)
            for tenant in self.tenants:
                self._try_wrapper(self.tenants_client.delete_tenant, tenant)
            for role in self.roles:
                self._try_wrapper(self.roles_client.delete_role, role)
            for v3_user in self.v3_users:
                self._try_wrapper(self.client.delete_user, v3_user)
            for v3_project in self.projects:
                self._try_wrapper(self.client.delete_project, v3_project)
            for v3_role in self.v3_roles:
                self._try_wrapper(self.client.delete_role, v3_role)
            for domain in self.domains:
                self._try_wrapper(self.client.update_domain, domain,
                                  enabled=False)
                self._try_wrapper(self.client.delete_domain, domain)
