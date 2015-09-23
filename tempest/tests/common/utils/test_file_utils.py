# Copyright 2014 IBM Corp.
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

import mock

from tempest.common.utils import file_utils
from tempest.tests import base


class TestFileUtils(base.TestCase):

    def test_have_effective_read_path(self):
        with mock.patch('six.moves.builtins.open', mock.mock_open(),
                        create=True):
            result = file_utils.have_effective_read_access('fake_path')
        self.assertTrue(result)

    def test_not_effective_read_path(self):
        result = file_utils.have_effective_read_access('fake_path')
        self.assertFalse(result)
