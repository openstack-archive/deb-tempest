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

import six

from tempest.api.compute.security_groups import base
from tempest import config
from tempest import test

CONF = config.CONF


class SecurityGroupRulesTestJSON(base.BaseSecurityGroupsTest):

    @classmethod
    def resource_setup(cls):
        super(SecurityGroupRulesTestJSON, cls).resource_setup()
        cls.client = cls.security_groups_client
        cls.neutron_available = CONF.service_available.neutron
        cls.ip_protocol = 'tcp'
        cls.from_port = 22
        cls.to_port = 22

    def setUp(cls):
        super(SecurityGroupRulesTestJSON, cls).setUp()

        from_port = cls.from_port
        to_port = cls.to_port
        group = {}
        ip_range = {}
        if cls._interface == 'xml':
            # NOTE: An XML response is different from the one of JSON
            # like the following.
            from_port = six.text_type(from_port)
            to_port = six.text_type(to_port)
            group = {'tenant_id': 'None', 'name': 'None'}
            ip_range = {'cidr': 'None'}
        cls.expected = {
            'id': None,
            'parent_group_id': None,
            'ip_protocol': cls.ip_protocol,
            'from_port': from_port,
            'to_port': to_port,
            'ip_range': ip_range,
            'group': group
        }

    def _check_expected_response(self, actual_rule):
        for key in self.expected:
            if key == 'id':
                continue
            self.assertEqual(self.expected[key], actual_rule[key],
                             "Miss-matched key is %s" % key)

    @test.attr(type='smoke')
    @test.services('network')
    def test_security_group_rules_create(self):
        # Positive test: Creation of Security Group rule
        # should be successful
        # Creating a Security Group to add rules to it
        _, security_group = self.create_security_group()
        securitygroup_id = security_group['id']
        # Adding rules to the created Security Group
        _, rule = \
            self.client.create_security_group_rule(securitygroup_id,
                                                   self.ip_protocol,
                                                   self.from_port,
                                                   self.to_port)
        self.expected['parent_group_id'] = securitygroup_id
        self.expected['ip_range'] = {'cidr': '0.0.0.0/0'}
        self._check_expected_response(rule)

    @test.attr(type='smoke')
    @test.services('network')
    def test_security_group_rules_create_with_optional_cidr(self):
        # Positive test: Creation of Security Group rule
        # with optional argument cidr
        # should be successful

        # Creating a Security Group to add rules to it
        _, security_group = self.create_security_group()
        parent_group_id = security_group['id']

        # Adding rules to the created Security Group with optional cidr
        cidr = '10.2.3.124/24'
        _, rule = \
            self.client.create_security_group_rule(parent_group_id,
                                                   self.ip_protocol,
                                                   self.from_port,
                                                   self.to_port,
                                                   cidr=cidr)
        self.expected['parent_group_id'] = parent_group_id
        self.expected['ip_range'] = {'cidr': cidr}
        self._check_expected_response(rule)

    @test.attr(type='smoke')
    @test.services('network')
    def test_security_group_rules_create_with_optional_group_id(self):
        # Positive test: Creation of Security Group rule
        # with optional argument group_id
        # should be successful

        # Creating a Security Group to add rules to it
        _, security_group = self.create_security_group()
        parent_group_id = security_group['id']

        # Creating a Security Group so as to assign group_id to the rule
        _, security_group = self.create_security_group()
        group_id = security_group['id']
        group_name = security_group['name']

        # Adding rules to the created Security Group with optional group_id
        _, rule = \
            self.client.create_security_group_rule(parent_group_id,
                                                   self.ip_protocol,
                                                   self.from_port,
                                                   self.to_port,
                                                   group_id=group_id)
        self.expected['parent_group_id'] = parent_group_id
        self.expected['group'] = {'tenant_id': self.client.tenant_id,
                                  'name': group_name}
        self._check_expected_response(rule)

    @test.attr(type='smoke')
    @test.services('network')
    def test_security_group_rules_list(self):
        # Positive test: Created Security Group rules should be
        # in the list of all rules
        # Creating a Security Group to add rules to it
        resp, security_group = self.create_security_group()
        securitygroup_id = security_group['id']

        # Add a first rule to the created Security Group
        resp, rule = \
            self.client.create_security_group_rule(securitygroup_id,
                                                   self.ip_protocol,
                                                   self.from_port,
                                                   self.to_port)
        rule1_id = rule['id']

        # Add a second rule to the created Security Group
        ip_protocol2 = 'icmp'
        from_port2 = -1
        to_port2 = -1
        resp, rule = \
            self.client.create_security_group_rule(securitygroup_id,
                                                   ip_protocol2,
                                                   from_port2, to_port2)
        rule2_id = rule['id']
        # Delete the Security Group rule2 at the end of this method
        self.addCleanup(self.client.delete_security_group_rule, rule2_id)

        # Get rules of the created Security Group
        resp, rules = \
            self.client.list_security_group_rules(securitygroup_id)
        self.assertTrue(any([i for i in rules if i['id'] == rule1_id]))
        self.assertTrue(any([i for i in rules if i['id'] == rule2_id]))

    @test.attr(type='smoke')
    @test.services('network')
    def test_security_group_rules_delete_when_peer_group_deleted(self):
        # Positive test:rule will delete when peer group deleting
        # Creating a Security Group to add rules to it
        resp, security_group = self.create_security_group()
        sg1_id = security_group['id']
        # Creating other Security Group to access to group1
        resp, security_group = self.create_security_group()
        sg2_id = security_group['id']
        # Adding rules to the Group1
        resp, rule = \
            self.client.create_security_group_rule(sg1_id,
                                                   self.ip_protocol,
                                                   self.from_port,
                                                   self.to_port,
                                                   group_id=sg2_id)

        self.assertEqual(200, resp.status)
        # Delete group2
        resp, body = self.client.delete_security_group(sg2_id)
        self.assertEqual(202, resp.status)
        # Get rules of the Group1
        resp, rules = \
            self.client.list_security_group_rules(sg1_id)
        # The group1 has no rules because group2 has deleted
        self.assertEqual(0, len(rules))


class SecurityGroupRulesTestXML(SecurityGroupRulesTestJSON):
    _interface = 'xml'
