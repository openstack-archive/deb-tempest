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


from tempest.api.identity import base
from tempest.common.utils import data_utils
from tempest import test


class DomainsTestJSON(base.BaseIdentityV3AdminTest):
    _interface = 'json'

    def _delete_domain(self, domain_id):
        # It is necessary to disable the domain before deleting,
        # or else it would result in unauthorized error
        self.client.update_domain(domain_id, enabled=False)
        self.client.delete_domain(domain_id)

    @test.attr(type='smoke')
    def test_list_domains(self):
        # Test to list domains
        domain_ids = list()
        fetched_ids = list()
        for _ in range(3):
            _, domain = self.client.create_domain(
                data_utils.rand_name('domain-'),
                description=data_utils.rand_name('domain-desc-'))
            # Delete the domain at the end of this method
            self.addCleanup(self._delete_domain, domain['id'])
            domain_ids.append(domain['id'])
        # List and Verify Domains
        _, body = self.client.list_domains()
        for d in body:
            fetched_ids.append(d['id'])
        missing_doms = [d for d in domain_ids if d not in fetched_ids]
        self.assertEqual(0, len(missing_doms))

    @test.attr(type='smoke')
    def test_create_update_delete_domain(self):
        d_name = data_utils.rand_name('domain-')
        d_desc = data_utils.rand_name('domain-desc-')
        _, domain = self.client.create_domain(
            d_name, description=d_desc)
        self.addCleanup(self._delete_domain, domain['id'])
        self.assertIn('id', domain)
        self.assertIn('description', domain)
        self.assertIn('name', domain)
        self.assertIn('enabled', domain)
        self.assertIn('links', domain)
        self.assertIsNotNone(domain['id'])
        self.assertEqual(d_name, domain['name'])
        self.assertEqual(d_desc, domain['description'])
        if self._interface == "json":
            self.assertEqual(True, domain['enabled'])
        else:
            self.assertEqual('true', str(domain['enabled']).lower())
        new_desc = data_utils.rand_name('new-desc-')
        new_name = data_utils.rand_name('new-name-')

        _, updated_domain = self.client.update_domain(
            domain['id'], name=new_name, description=new_desc)
        self.assertIn('id', updated_domain)
        self.assertIn('description', updated_domain)
        self.assertIn('name', updated_domain)
        self.assertIn('enabled', updated_domain)
        self.assertIn('links', updated_domain)
        self.assertIsNotNone(updated_domain['id'])
        self.assertEqual(new_name, updated_domain['name'])
        self.assertEqual(new_desc, updated_domain['description'])
        self.assertEqual('true', str(updated_domain['enabled']).lower())

        _, fetched_domain = self.client.get_domain(domain['id'])
        self.assertEqual(new_name, fetched_domain['name'])
        self.assertEqual(new_desc, fetched_domain['description'])
        self.assertEqual('true', str(fetched_domain['enabled']).lower())


class DomainsTestXML(DomainsTestJSON):
    _interface = 'xml'
