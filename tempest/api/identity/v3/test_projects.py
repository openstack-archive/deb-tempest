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


class IdentityV3ProjectsTest(base.BaseIdentityV3Test):

    credentials = ['primary', 'alt']

    @test.idempotent_id('86128d46-e170-4644-866a-cc487f699e1d')
    def test_list_projects_returns_only_authorized_projects(self):
        alt_project_name =\
            self.alt_manager.credentials.credentials.project_name
        resp = self.non_admin_client.list_user_projects(
            self.os.credentials.user_id)

        # check that user can see only that projects that he presents in so
        # user can successfully authenticate using his credentials and
        # project name from received projects list
        for project in resp['projects']:
            token_id, body = self.non_admin_token.get_token(
                username=self.os.credentials.username,
                password=self.os.credentials.password,
                project_name=project['name'],
                auth_data=True)
            self.assertNotEmpty(token_id)
            self.assertEqual(body['project']['id'], project['id'])
            self.assertEqual(body['project']['name'], project['name'])
            self.assertEqual(body['user']['id'], self.os.credentials.user_id)

        # check that user cannot log in to alt user's project
        self.assertRaises(
            lib_exc.Unauthorized,
            self.non_admin_token.get_token,
            username=self.os.credentials.username,
            password=self.os.credentials.password,
            project_name=alt_project_name)
