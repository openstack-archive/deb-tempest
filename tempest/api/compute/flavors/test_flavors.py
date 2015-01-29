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

from tempest.api.compute import base
from tempest import test


class FlavorsV3Test(base.BaseComputeTest):

    _api_version = 3
    _min_disk = 'min_disk'
    _min_ram = 'min_ram'

    @classmethod
    def resource_setup(cls):
        super(FlavorsV3Test, cls).resource_setup()
        cls.client = cls.flavors_client

    @test.attr(type='smoke')
    def test_list_flavors(self):
        # List of all flavors should contain the expected flavor
        resp, flavors = self.client.list_flavors()
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_min_detail = {'id': flavor['id'], 'links': flavor['links'],
                             'name': flavor['name']}
        self.assertIn(flavor_min_detail, flavors)

    @test.attr(type='smoke')
    def test_list_flavors_with_detail(self):
        # Detailed list of all flavors should contain the expected flavor
        resp, flavors = self.client.list_flavors_with_detail()
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        self.assertIn(flavor, flavors)

    @test.attr(type='smoke')
    def test_get_flavor(self):
        # The expected flavor details should be returned
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        self.assertEqual(self.flavor_ref, flavor['id'])

    @test.attr(type='gate')
    def test_list_flavors_limit_results(self):
        # Only the expected number of flavors should be returned
        params = {'limit': 1}
        resp, flavors = self.client.list_flavors(params)
        self.assertEqual(1, len(flavors))

    @test.attr(type='gate')
    def test_list_flavors_detailed_limit_results(self):
        # Only the expected number of flavors (detailed) should be returned
        params = {'limit': 1}
        resp, flavors = self.client.list_flavors_with_detail(params)
        self.assertEqual(1, len(flavors))

    @test.attr(type='gate')
    def test_list_flavors_using_marker(self):
        # The list of flavors should start from the provided marker
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_id = flavor['id']

        params = {'marker': flavor_id}
        resp, flavors = self.client.list_flavors(params)
        self.assertFalse(any([i for i in flavors if i['id'] == flavor_id]),
                         'The list of flavors did not start after the marker.')

    @test.attr(type='gate')
    def test_list_flavors_detailed_using_marker(self):
        # The list of flavors should start from the provided marker
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_id = flavor['id']

        params = {'marker': flavor_id}
        resp, flavors = self.client.list_flavors_with_detail(params)
        self.assertFalse(any([i for i in flavors if i['id'] == flavor_id]),
                         'The list of flavors did not start after the marker.')

    @test.attr(type='gate')
    def test_list_flavors_detailed_filter_by_min_disk(self):
        # The detailed list of flavors should be filtered by disk space
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_id = flavor['id']

        params = {self._min_disk: flavor['disk'] + 1}
        resp, flavors = self.client.list_flavors_with_detail(params)
        self.assertFalse(any([i for i in flavors if i['id'] == flavor_id]))

    @test.attr(type='gate')
    def test_list_flavors_detailed_filter_by_min_ram(self):
        # The detailed list of flavors should be filtered by RAM
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_id = flavor['id']

        params = {self._min_ram: flavor['ram'] + 1}
        resp, flavors = self.client.list_flavors_with_detail(params)
        self.assertFalse(any([i for i in flavors if i['id'] == flavor_id]))

    @test.attr(type='gate')
    def test_list_flavors_filter_by_min_disk(self):
        # The list of flavors should be filtered by disk space
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_id = flavor['id']

        params = {self._min_disk: flavor['disk'] + 1}
        resp, flavors = self.client.list_flavors(params)
        self.assertFalse(any([i for i in flavors if i['id'] == flavor_id]))

    @test.attr(type='gate')
    def test_list_flavors_filter_by_min_ram(self):
        # The list of flavors should be filtered by RAM
        resp, flavor = self.client.get_flavor_details(self.flavor_ref)
        flavor_id = flavor['id']

        params = {self._min_ram: flavor['ram'] + 1}
        resp, flavors = self.client.list_flavors(params)
        self.assertFalse(any([i for i in flavors if i['id'] == flavor_id]))


class FlavorsV2TestJSON(FlavorsV3Test):

    _api_version = 2
    _min_disk = 'minDisk'
    _min_ram = 'minRam'


class FlavorsV2TestXML(FlavorsV2TestJSON):
    _interface = 'xml'
