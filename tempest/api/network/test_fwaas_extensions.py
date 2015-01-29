# Copyright 2014 NEC Corporation. All rights reserved.
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

from tempest.api.network import base
from tempest.common.utils import data_utils
from tempest import config
from tempest import exceptions
from tempest import test

CONF = config.CONF


class FWaaSExtensionTestJSON(base.BaseNetworkTest):
    _interface = 'json'

    """
    Tests the following operations in the Neutron API using the REST client for
    Neutron:

        List firewall rules
        Create firewall rule
        Update firewall rule
        Delete firewall rule
        Show firewall rule
        List firewall policies
        Create firewall policy
        Update firewall policy
        Insert firewall rule to policy
        Remove firewall rule from policy
        Delete firewall policy
        Show firewall policy
        List firewall
        Create firewall
        Update firewall
        Delete firewall
        Show firewall
    """

    @classmethod
    def resource_setup(cls):
        super(FWaaSExtensionTestJSON, cls).resource_setup()
        if not test.is_extension_enabled('fwaas', 'network'):
            msg = "FWaaS Extension not enabled."
            raise cls.skipException(msg)
        cls.fw_rule = cls.create_firewall_rule("allow", "tcp")
        cls.fw_policy = cls.create_firewall_policy()

    def _try_delete_policy(self, policy_id):
        # delete policy, if it exists
        try:
            self.client.delete_firewall_policy(policy_id)
        # if policy is not found, this means it was deleted in the test
        except exceptions.NotFound:
            pass

    def _try_delete_rule(self, rule_id):
        # delete rule, if it exists
        try:
            self.client.delete_firewall_rule(rule_id)
        # if rule is not found, this means it was deleted in the test
        except exceptions.NotFound:
            pass

    def _try_delete_firewall(self, fw_id):
        # delete firewall, if it exists
        try:
            self.client.delete_firewall(fw_id)
        # if firewall is not found, this means it was deleted in the test
        except exceptions.NotFound:
            pass

        self.client.wait_for_resource_deletion('firewall', fw_id)

    def _wait_until_ready(self, fw_id):
        target_states = ('ACTIVE', 'CREATED')

        def _wait():
            _, firewall = self.client.show_firewall(fw_id)
            firewall = firewall['firewall']
            return firewall['status'] in target_states

        if not test.call_until_true(_wait, CONF.network.build_timeout,
                                    CONF.network.build_interval):
            m = ("Timed out waiting for firewall %s to reach %s state(s)" %
                 (fw_id, target_states))
            raise exceptions.TimeoutException(m)

    def test_list_firewall_rules(self):
        # List firewall rules
        _, fw_rules = self.client.list_firewall_rules()
        fw_rules = fw_rules['firewall_rules']
        self.assertIn((self.fw_rule['id'],
                       self.fw_rule['name'],
                       self.fw_rule['action'],
                       self.fw_rule['protocol'],
                       self.fw_rule['ip_version'],
                       self.fw_rule['enabled']),
                      [(m['id'],
                        m['name'],
                        m['action'],
                        m['protocol'],
                        m['ip_version'],
                        m['enabled']) for m in fw_rules])

    def test_create_update_delete_firewall_rule(self):
        # Create firewall rule
        _, body = self.client.create_firewall_rule(
            name=data_utils.rand_name("fw-rule"),
            action="allow",
            protocol="tcp")
        fw_rule_id = body['firewall_rule']['id']

        # Update firewall rule
        _, body = self.client.update_firewall_rule(fw_rule_id,
                                                   shared=True)
        self.assertTrue(body["firewall_rule"]['shared'])

        # Delete firewall rule
        self.client.delete_firewall_rule(fw_rule_id)
        # Confirm deletion
        resp, fw_rules = self.client.list_firewall_rules()
        self.assertNotIn(fw_rule_id,
                         [m['id'] for m in fw_rules['firewall_rules']])

    def test_show_firewall_rule(self):
        # show a created firewall rule
        _, fw_rule = self.client.show_firewall_rule(self.fw_rule['id'])
        for key, value in fw_rule['firewall_rule'].iteritems():
            self.assertEqual(self.fw_rule[key], value)

    def test_list_firewall_policies(self):
        _, fw_policies = self.client.list_firewall_policies()
        fw_policies = fw_policies['firewall_policies']
        self.assertIn((self.fw_policy['id'],
                       self.fw_policy['name'],
                       self.fw_policy['firewall_rules']),
                      [(m['id'],
                        m['name'],
                        m['firewall_rules']) for m in fw_policies])

    def test_create_update_delete_firewall_policy(self):
        # Create firewall policy
        _, body = self.client.create_firewall_policy(
            name=data_utils.rand_name("fw-policy"))
        fw_policy_id = body['firewall_policy']['id']
        self.addCleanup(self._try_delete_policy, fw_policy_id)

        # Update firewall policy
        _, body = self.client.update_firewall_policy(fw_policy_id,
                                                     shared=True,
                                                     name="updated_policy")
        updated_fw_policy = body["firewall_policy"]
        self.assertTrue(updated_fw_policy['shared'])
        self.assertEqual("updated_policy", updated_fw_policy['name'])

        # Delete firewall policy
        self.client.delete_firewall_policy(fw_policy_id)
        # Confirm deletion
        resp, fw_policies = self.client.list_firewall_policies()
        fw_policies = fw_policies['firewall_policies']
        self.assertNotIn(fw_policy_id, [m['id'] for m in fw_policies])

    def test_show_firewall_policy(self):
        # show a created firewall policy
        _, fw_policy = self.client.show_firewall_policy(self.fw_policy['id'])
        fw_policy = fw_policy['firewall_policy']
        for key, value in fw_policy.iteritems():
            self.assertEqual(self.fw_policy[key], value)

    def test_create_show_delete_firewall(self):
        # Create tenant network resources required for an ACTIVE firewall
        network = self.create_network()
        subnet = self.create_subnet(network)
        router = self.create_router(
            data_utils.rand_name('router-'),
            admin_state_up=True)
        self.client.add_router_interface_with_subnet_id(
            router['id'], subnet['id'])

        # Create firewall
        _, body = self.client.create_firewall(
            name=data_utils.rand_name("firewall"),
            firewall_policy_id=self.fw_policy['id'])
        created_firewall = body['firewall']
        firewall_id = created_firewall['id']
        self.addCleanup(self._try_delete_firewall, firewall_id)

        # Wait for the firewall resource to become ready
        self._wait_until_ready(firewall_id)

        # show a created firewall
        _, firewall = self.client.show_firewall(firewall_id)
        firewall = firewall['firewall']

        for key, value in firewall.iteritems():
            if key == 'status':
                continue
            self.assertEqual(created_firewall[key], value)

        # list firewall
        _, firewalls = self.client.list_firewalls()
        firewalls = firewalls['firewalls']
        self.assertIn((created_firewall['id'],
                       created_firewall['name'],
                       created_firewall['firewall_policy_id']),
                      [(m['id'],
                        m['name'],
                        m['firewall_policy_id']) for m in firewalls])

        # Delete firewall
        self.client.delete_firewall(firewall_id)

    @test.attr(type='smoke')
    def test_insert_remove_firewall_rule_from_policy(self):
        # Create firewall rule
        resp, body = self.client.create_firewall_rule(
            name=data_utils.rand_name("fw-rule"),
            action="allow",
            protocol="tcp")
        fw_rule_id = body['firewall_rule']['id']
        self.addCleanup(self._try_delete_rule, fw_rule_id)
        # Create firewall policy
        _, body = self.client.create_firewall_policy(
            name=data_utils.rand_name("fw-policy"))
        fw_policy_id = body['firewall_policy']['id']
        self.addCleanup(self._try_delete_policy, fw_policy_id)

        # Insert rule to firewall policy
        self.client.insert_firewall_rule_in_policy(
            fw_policy_id, fw_rule_id, '', '')

        # Verify insertion of rule in policy
        self.assertIn(fw_rule_id, self._get_list_fw_rule_ids(fw_policy_id))
        # Remove rule from the firewall policy
        self.client.remove_firewall_rule_from_policy(
            fw_policy_id, fw_rule_id)

        # Verify removal of rule from firewall policy
        self.assertNotIn(fw_rule_id, self._get_list_fw_rule_ids(fw_policy_id))

    def _get_list_fw_rule_ids(self, fw_policy_id):
        _, fw_policy = self.client.show_firewall_policy(
            fw_policy_id)
        return [ruleid for ruleid in fw_policy['firewall_policy']
                ['firewall_rules']]


class FWaaSExtensionTestXML(FWaaSExtensionTestJSON):
    _interface = 'xml'
