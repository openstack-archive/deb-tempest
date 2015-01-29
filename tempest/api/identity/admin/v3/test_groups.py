# Copyright 2013 IBM Corp.
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


class GroupsV3TestJSON(base.BaseIdentityV3AdminTest):
    _interface = 'json'

    @classmethod
    def resource_setup(cls):
        super(GroupsV3TestJSON, cls).resource_setup()

    @test.attr(type='smoke')
    def test_group_create_update_get(self):
        name = data_utils.rand_name('Group')
        description = data_utils.rand_name('Description')
        _, group = self.client.create_group(name,
                                            description=description)
        self.addCleanup(self.client.delete_group, group['id'])
        self.assertEqual(group['name'], name)
        self.assertEqual(group['description'], description)

        new_name = data_utils.rand_name('UpdateGroup')
        new_desc = data_utils.rand_name('UpdateDescription')
        _, updated_group = self.client.update_group(group['id'],
                                                    name=new_name,
                                                    description=new_desc)
        self.assertEqual(updated_group['name'], new_name)
        self.assertEqual(updated_group['description'], new_desc)

        _, new_group = self.client.get_group(group['id'])
        self.assertEqual(group['id'], new_group['id'])
        self.assertEqual(new_name, new_group['name'])
        self.assertEqual(new_desc, new_group['description'])

    @test.attr(type='smoke')
    def test_group_users_add_list_delete(self):
        name = data_utils.rand_name('Group')
        _, group = self.client.create_group(name)
        self.addCleanup(self.client.delete_group, group['id'])
        # add user into group
        users = []
        for i in range(3):
            name = data_utils.rand_name('User')
            _, user = self.client.create_user(name)
            users.append(user)
            self.addCleanup(self.client.delete_user, user['id'])
            self.client.add_group_user(group['id'], user['id'])

        # list users in group
        _, group_users = self.client.list_group_users(group['id'])
        self.assertEqual(sorted(users), sorted(group_users))
        # delete user in group
        for user in users:
            self.client.delete_group_user(group['id'],
                                          user['id'])
        _, group_users = self.client.list_group_users(group['id'])
        self.assertEqual(len(group_users), 0)

    @test.attr(type='smoke')
    def test_list_user_groups(self):
        # create a user
        _, user = self.client.create_user(
            data_utils.rand_name('User-'),
            password=data_utils.rand_name('Pass-'))
        self.addCleanup(self.client.delete_user, user['id'])
        # create two groups, and add user into them
        groups = []
        for i in range(2):
            name = data_utils.rand_name('Group-')
            _, group = self.client.create_group(name)
            groups.append(group)
            self.addCleanup(self.client.delete_group, group['id'])
            self.client.add_group_user(group['id'], user['id'])
        # list groups which user belongs to
        _, user_groups = self.client.list_user_groups(user['id'])
        self.assertEqual(sorted(groups), sorted(user_groups))
        self.assertEqual(2, len(user_groups))


class GroupsV3TestXML(GroupsV3TestJSON):
    _interface = 'xml'
