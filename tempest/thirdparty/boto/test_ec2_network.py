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

from tempest import test
from tempest.thirdparty.boto import test as boto_test


class EC2NetworkTest(boto_test.BotoTestCase):

    @classmethod
    def resource_setup(cls):
        super(EC2NetworkTest, cls).resource_setup()
        cls.client = cls.os.ec2api_client

    # Note(afazekas): these tests for things duable without an instance
    @test.skip_because(bug="1080406")
    def test_disassociate_not_associated_floating_ip(self):
        # EC2 disassociate not associated floating ip
        ec2_codes = self.ec2_error_code
        address = self.client.allocate_address()
        public_ip = address.public_ip
        rcuk = self.addResourceCleanUp(self.client.release_address, public_ip)
        addresses_get = self.client.get_all_addresses(addresses=(public_ip,))
        self.assertEqual(len(addresses_get), 1)
        self.assertEqual(addresses_get[0].public_ip, public_ip)
        self.assertBotoError(ec2_codes.client.InvalidAssociationID.NotFound,
                             address.disassociate)
        self.client.release_address(public_ip)
        self.cancelResourceCleanUp(rcuk)
        self.assertAddressReleasedWait(address)
