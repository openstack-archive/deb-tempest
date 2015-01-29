# Copyright 2014 Hewlett-Packard Development Company, L.P.
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

import copy

from oslo.config import cfg

from tempest import auth
from tempest.common import http
from tempest.common import tempest_fixtures as fixtures
from tempest import config
from tempest import exceptions
from tempest.tests import base
from tempest.tests import fake_config
from tempest.tests import fake_http
from tempest.tests import fake_identity


class CredentialsTests(base.TestCase):
    attributes = {}
    credentials_class = auth.Credentials

    def _get_credentials(self, attributes=None):
        if attributes is None:
            attributes = self.attributes
        return self.credentials_class(**attributes)

    def setUp(self):
        super(CredentialsTests, self).setUp()
        self.fake_http = fake_http.fake_httplib2(return_type=200)
        self.stubs.Set(http.ClosingHttp, 'request', self.fake_http.request)
        self.useFixture(fake_config.ConfigFixture())
        self.stubs.Set(config, 'TempestConfigPrivate', fake_config.FakePrivate)

    def test_create(self):
        creds = self._get_credentials()
        self.assertEqual(self.attributes, creds._initial)

    def test_create_invalid_attr(self):
        self.assertRaises(exceptions.InvalidCredentials,
                          self._get_credentials,
                          attributes=dict(invalid='fake'))

    def test_default(self):
        self.useFixture(fixtures.LockFixture('auth_version'))
        for ctype in self.credentials_class.TYPES:
            self.assertRaises(NotImplementedError,
                              self.credentials_class.get_default,
                              credentials_type=ctype)

    def test_invalid_default(self):
        self.assertRaises(exceptions.InvalidCredentials,
                          auth.Credentials.get_default,
                          credentials_type='invalid_type')

    def test_is_valid(self):
        creds = self._get_credentials()
        self.assertRaises(NotImplementedError, creds.is_valid)


class KeystoneV2CredentialsTests(CredentialsTests):
    attributes = {
        'username': 'fake_username',
        'password': 'fake_password',
        'tenant_name': 'fake_tenant_name'
    }

    identity_response = fake_identity._fake_v2_response
    credentials_class = auth.KeystoneV2Credentials

    def setUp(self):
        super(KeystoneV2CredentialsTests, self).setUp()
        self.stubs.Set(http.ClosingHttp, 'request', self.identity_response)
        self.stubs.Set(config, 'TempestConfigPrivate', fake_config.FakePrivate)

    def _verify_credentials(self, credentials_class, filled=True,
                            creds_dict=None):

        def _check(credentials):
            # Check the right version of credentials has been returned
            self.assertIsInstance(credentials, credentials_class)
            # Check the id attributes are filled in
            attributes = [x for x in credentials.ATTRIBUTES if (
                '_id' in x and x != 'domain_id')]
            for attr in attributes:
                if filled:
                    self.assertIsNotNone(getattr(credentials, attr))
                else:
                    self.assertIsNone(getattr(credentials, attr))

        if creds_dict is None:
            for ctype in auth.Credentials.TYPES:
                creds = auth.get_default_credentials(credential_type=ctype,
                                                     fill_in=filled)
                _check(creds)
        else:
            creds = auth.get_credentials(fill_in=filled, **creds_dict)
            _check(creds)

    def test_get_default_credentials(self):
        self.useFixture(fixtures.LockFixture('auth_version'))
        self._verify_credentials(credentials_class=self.credentials_class)

    def test_get_credentials(self):
        self.useFixture(fixtures.LockFixture('auth_version'))
        self._verify_credentials(credentials_class=self.credentials_class,
                                 creds_dict=self.attributes)

    def test_get_credentials_not_filled(self):
        self.useFixture(fixtures.LockFixture('auth_version'))
        self._verify_credentials(credentials_class=self.credentials_class,
                                 filled=False,
                                 creds_dict=self.attributes)

    def test_is_valid(self):
        creds = self._get_credentials()
        self.assertTrue(creds.is_valid())

    def _test_is_not_valid(self, ignore_key):
        creds = self._get_credentials()
        for attr in self.attributes.keys():
            if attr == ignore_key:
                continue
            temp_attr = getattr(creds, attr)
            delattr(creds, attr)
            self.assertFalse(creds.is_valid(),
                             "Credentials should be invalid without %s" % attr)
            setattr(creds, attr, temp_attr)

    def test_is_not_valid(self):
        # NOTE(mtreinish): A KeystoneV2 credential object is valid without
        # a tenant_name. So skip that check. See tempest.auth for the valid
        # credential requirements
        self._test_is_not_valid('tenant_name')

    def test_default(self):
        self.useFixture(fixtures.LockFixture('auth_version'))
        for ctype in self.credentials_class.TYPES:
            creds = self.credentials_class.get_default(credentials_type=ctype)
            for attr in self.attributes.keys():
                # Default configuration values related to credentials
                # are defined as fake_* in fake_config.py
                self.assertEqual(getattr(creds, attr), 'fake_' + attr)

    def test_reset_all_attributes(self):
        creds = self._get_credentials()
        initial_creds = copy.deepcopy(creds)
        set_attr = creds.__dict__.keys()
        missing_attr = set(creds.ATTRIBUTES).difference(set_attr)
        # Set all unset attributes, then reset
        for attr in missing_attr:
            setattr(creds, attr, 'fake' + attr)
        creds.reset()
        # Check reset credentials are same as initial ones
        self.assertEqual(creds, initial_creds)

    def test_reset_single_attribute(self):
        creds = self._get_credentials()
        initial_creds = copy.deepcopy(creds)
        set_attr = creds.__dict__.keys()
        missing_attr = set(creds.ATTRIBUTES).difference(set_attr)
        # Set one unset attributes, then reset
        for attr in missing_attr:
            setattr(creds, attr, 'fake' + attr)
            creds.reset()
            # Check reset credentials are same as initial ones
            self.assertEqual(creds, initial_creds)


class KeystoneV3CredentialsTests(KeystoneV2CredentialsTests):
    attributes = {
        'username': 'fake_username',
        'password': 'fake_password',
        'project_name': 'fake_project_name',
        'user_domain_name': 'fake_domain_name'
    }

    credentials_class = auth.KeystoneV3Credentials
    identity_response = fake_identity._fake_v3_response

    def setUp(self):
        super(KeystoneV3CredentialsTests, self).setUp()
        # Additional config items reset by cfg fixture after each test
        cfg.CONF.set_default('auth_version', 'v3', group='identity')
        # Identity group items
        for prefix in ['', 'alt_', 'admin_']:
            cfg.CONF.set_default(prefix + 'domain_name', 'fake_domain_name',
                                 group='identity')
        # Compute Admin group items
        cfg.CONF.set_default('domain_name', 'fake_domain_name',
                             group='compute-admin')

    def test_default(self):
        self.useFixture(fixtures.LockFixture('auth_version'))
        for ctype in self.credentials_class.TYPES:
            creds = self.credentials_class.get_default(credentials_type=ctype)
            for attr in self.attributes.keys():
                if attr == 'project_name':
                    config_value = 'fake_tenant_name'
                elif attr == 'user_domain_name':
                    config_value = 'fake_domain_name'
                else:
                    config_value = 'fake_' + attr
                self.assertEqual(getattr(creds, attr), config_value)

    def test_is_not_valid(self):
        # NOTE(mtreinish) For a Keystone V3 credential object a project name
        # is not required to be valid, so we skip that check. See tempest.auth
        # for the valid credential requirements
        self._test_is_not_valid('project_name')

    def test_synced_attributes(self):
        attributes = self.attributes
        # Create V3 credentials with tenant instead of project, and user_domain
        for attr in ['project_id', 'user_domain_id']:
            attributes[attr] = 'fake_' + attr
        creds = self._get_credentials(attributes)
        self.assertEqual(creds.project_name, creds.tenant_name)
        self.assertEqual(creds.project_id, creds.tenant_id)
        self.assertEqual(creds.user_domain_name, creds.project_domain_name)
        self.assertEqual(creds.user_domain_id, creds.project_domain_id)
        # Replace user_domain with project_domain
        del attributes['user_domain_name']
        del attributes['user_domain_id']
        del attributes['project_name']
        del attributes['project_id']
        for attr in ['project_domain_name', 'project_domain_id',
                     'tenant_name', 'tenant_id']:
            attributes[attr] = 'fake_' + attr
        self.assertEqual(creds.tenant_name, creds.project_name)
        self.assertEqual(creds.tenant_id, creds.project_id)
        self.assertEqual(creds.project_domain_name, creds.user_domain_name)
        self.assertEqual(creds.project_domain_id, creds.user_domain_id)
