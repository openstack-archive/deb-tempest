# Copyright 2015 IBM Corp.
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
from tempest.services.compute.json import servers_client
from tempest.tests import fake_auth_provider
from tempest.tests.services.compute import base


class TestServersClient(base.BaseComputeServiceTest):

    FAKE_SERVERS = {'servers': [{
        "id": "616fb98f-46ca-475e-917e-2563e5a8cd19",
        "links": [
            {
                "href": "http://os.co/v2/616fb98f-46ca-475e-917e-2563e5a8cd19",
                "rel": "self"
            },
            {
                "href": "http://os.co/616fb98f-46ca-475e-917e-2563e5a8cd19",
                "rel": "bookmark"
            }
        ],
        "name": u"new\u1234-server-test"}]
    }

    FAKE_SERVER_DIAGNOSTICS = {
        "cpu0_time": 17300000000,
        "memory": 524288,
        "vda_errors": -1,
        "vda_read": 262144,
        "vda_read_req": 112,
        "vda_write": 5778432,
        "vda_write_req": 488,
        "vnet1_rx": 2070139,
        "vnet1_rx_drop": 0,
        "vnet1_rx_errors": 0,
        "vnet1_rx_packets": 26701,
        "vnet1_tx": 140208,
        "vnet1_tx_drop": 0,
        "vnet1_tx_errors": 0,
        "vnet1_tx_packets": 662
    }

    FAKE_SERVER_GET = {'server': {
        "accessIPv4": "",
        "accessIPv6": "",
        "addresses": {
            "private": [
                {
                    "addr": "192.168.0.3",
                    "version": 4
                }
            ]
        },
        "created": "2012-08-20T21:11:09Z",
        "flavor": {
            "id": "1",
            "links": [
                {
                    "href": "http://os.com/openstack/flavors/1",
                    "rel": "bookmark"
                }
            ]
        },
        "hostId": "65201c14a29663e06d0748e561207d998b343e1d164bfa0aafa9c45d",
        "id": "893c7791-f1df-4c3d-8383-3caae9656c62",
        "image": {
            "id": "70a599e0-31e7-49b7-b260-868f441e862b",
            "links": [
                {
                    "href": "http://imgs/70a599e0-31e7-49b7-b260-868f441e862b",
                    "rel": "bookmark"
                }
            ]
        },
        "links": [
            {
                "href": "http://v2/srvs/893c7791-f1df-4c3d-8383-3caae9656c62",
                "rel": "self"
            },
            {
                "href": "http://srvs/893c7791-f1df-4c3d-8383-3caae9656c62",
                "rel": "bookmark"
            }
        ],
        "metadata": {
            u"My Server N\u1234me": u"Apa\u1234che1"
        },
        "name": u"new\u1234-server-test",
        "progress": 0,
        "status": "ACTIVE",
        "tenant_id": "openstack",
        "updated": "2012-08-20T21:11:09Z",
        "user_id": "fake"}
    }

    FAKE_SERVER_POST = {"server": {
        "id": "616fb98f-46ca-475e-917e-2563e5a8cd19",
        "adminPass": "fake-admin-pass",
        "security_groups": [
            'fake-security-group-1',
            'fake-security-group-2'
        ],
        "links": [
            {
                "href": "http://os.co/v2/616fb98f-46ca-475e-917e-2563e5a8cd19",
                "rel": "self"
            },
            {
                "href": "http://os.co/616fb98f-46ca-475e-917e-2563e5a8cd19",
                "rel": "bookmark"
            }
        ],
        "OS-DCF:diskConfig": "fake-disk-config"}
    }

    FAKE_ADDRESS = {"addresses": {
        "private": [
            {
                "addr": "192.168.0.3",
                "version": 4
            }
        ]}
    }

    FAKE_COMMON_VOLUME = {
        "id": "a6b0875b-6b5d-4a5a-81eb-0c3aa62e5fdb",
        "device": "fake-device",
        "volumeId": "a6b0875b-46ca-475e-917e-0c3aa62e5fdb",
        "serverId": "616fb98f-46ca-475e-917e-2563e5a8cd19"
    }

    FAKE_VIRTUAL_INTERFACES = {
        "id": "a6b0875b-46ca-475e-917e-0c3aa62e5fdb",
        "mac_address": "00:25:90:5b:f8:c3",
        "OS-EXT-VIF-NET:net_id": "fake-os-net-id"
    }

    FAKE_INSTANCE_ACTIONS = {
        "action": "fake-action",
        "request_id": "16fb98f-46ca-475e-917e-2563e5a8cd19",
        "user_id": "16fb98f-46ca-475e-917e-2563e5a8cd12",
        "project_id": "16fb98f-46ca-475e-917e-2563e5a8cd34",
        "start_time": "09MAR2015 11:15",
        "message": "fake-msg",
        "instance_uuid": "16fb98f-46ca-475e-917e-2563e5a8cd12"
    }

    FAKE_VNC_CONSOLE = {
        "type": "fake-type",
        "url": "http://os.co/v2/616fb98f-46ca-475e-917e-2563e5a8cd19"
    }

    FAKE_INSTANCE_ACTION_EVENTS = {
        "event": "fake-event",
        "start_time": "09MAR2015 11:15",
        "finish_time": "09MAR2015 11:15",
        "result": "fake-result",
        "traceback": "fake-trace-back"
    }

    FAKE_INSTANCE_WITH_EVENTS = copy.deepcopy(FAKE_INSTANCE_ACTIONS)
    FAKE_INSTANCE_WITH_EVENTS['events'] = [FAKE_INSTANCE_ACTION_EVENTS]

    FAKE_REBUILD_SERVER = copy.deepcopy(FAKE_SERVER_GET)
    FAKE_REBUILD_SERVER['server']['adminPass'] = 'fake-admin-pass'

    server_id = FAKE_SERVER_GET['server']['id']
    network_id = 'a6b0875b-6b5d-4a5a-81eb-0c3aa62e5fdb'

    def setUp(self):
        super(TestServersClient, self).setUp()
        fake_auth = fake_auth_provider.FakeAuthProvider()
        self.client = servers_client.ServersClient(
            fake_auth, 'compute', 'regionOne')

    def test_list_servers_with_str_body(self):
        self._test_list_servers()

    def test_list_servers_with_bytes_body(self):
        self._test_list_servers(bytes_body=True)

    def _test_list_servers(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_servers,
            'tempest.common.service_client.ServiceClient.get',
            self.FAKE_SERVERS,
            bytes_body)

    def test_show_server_with_str_body(self):
        self._test_show_server()

    def test_show_server_with_bytes_body(self):
        self._test_show_server(bytes_body=True)

    def _test_show_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.show_server,
            'tempest.common.service_client.ServiceClient.get',
            self.FAKE_SERVER_GET,
            bytes_body,
            server_id=self.server_id
            )

    def test_delete_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.delete_server,
            'tempest.common.service_client.ServiceClient.delete',
            {},
            status=204,
            server_id=self.server_id
            )

    def test_create_server_with_str_body(self):
        self._test_create_server()

    def test_create_server_with_bytes_body(self):
        self._test_create_server(True)

    def _test_create_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.create_server,
            'tempest.common.service_client.ServiceClient.post',
            self.FAKE_SERVER_POST,
            bytes_body,
            status=202,
            name='fake-name',
            imageRef='fake-image-ref',
            flavorRef='fake-flavor-ref'
            )

    def test_list_addresses_with_str_body(self):
        self._test_list_addresses()

    def test_list_addresses_with_bytes_body(self):
        self._test_list_addresses(True)

    def _test_list_addresses(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_addresses,
            'tempest.common.service_client.ServiceClient.get',
            self.FAKE_ADDRESS,
            bytes_body,
            server_id=self.server_id
            )

    def test_list_addresses_by_network_with_str_body(self):
        self._test_list_addresses_by_network()

    def test_list_addresses_by_network_with_bytes_body(self):
        self._test_list_addresses_by_network(True)

    def _test_list_addresses_by_network(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_addresses_by_network,
            'tempest.common.service_client.ServiceClient.get',
            self.FAKE_ADDRESS['addresses'],
            server_id=self.server_id,
            network_id=self.network_id
            )

    def test_action_with_str_body(self):
        self._test_action()

    def test_action_with_bytes_body(self):
        self._test_action(True)

    def _test_action(self, bytes_body=False):
        self.check_service_client_function(
            self.client.action,
            'tempest.common.service_client.ServiceClient.post',
            {},
            server_id=self.server_id,
            action_name='fake-action-name',
            schema={'status_code': 200}
            )

    def test_create_backup_with_str_body(self):
        self._test_create_backup()

    def test_create_backup_with_bytes_body(self):
        self._test_create_backup(True)

    def _test_create_backup(self, bytes_body=False):
        self.check_service_client_function(
            self.client.create_backup,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            backup_type='fake-backup',
            rotation='fake-rotation',
            name='fake-name'
            )

    def test_change_password_with_str_body(self):
        self._test_change_password()

    def test_change_password_with_bytes_body(self):
        self._test_change_password(True)

    def _test_change_password(self, bytes_body=False):
        self.check_service_client_function(
            self.client.change_password,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            adminPass='fake-admin-pass'
            )

    def test_show_password_with_str_body(self):
        self._test_show_password()

    def test_show_password_with_bytes_body(self):
        self._test_show_password(True)

    def _test_show_password(self, bytes_body=False):
        self.check_service_client_function(
            self.client.show_password,
            'tempest.common.service_client.ServiceClient.get',
            {'password': 'fake-password'},
            server_id=self.server_id
            )

    def test_delete_password_with_str_body(self):
        self._test_delete_password()

    def test_delete_password_with_bytes_body(self):
        self._test_delete_password(True)

    def _test_delete_password(self, bytes_body=False):
        self.check_service_client_function(
            self.client.delete_password,
            'tempest.common.service_client.ServiceClient.delete',
            {},
            status=204,
            server_id=self.server_id
            )

    def test_reboot_server_with_str_body(self):
        self._test_reboot_server()

    def test_reboot_server_with_bytes_body(self):
        self._test_reboot_server(True)

    def _test_reboot_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.reboot_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            type='fake-reboot-type'
            )

    def test_rebuild_server_with_str_body(self):
        self._test_rebuild_server()

    def test_rebuild_server_with_bytes_body(self):
        self._test_rebuild_server(True)

    def _test_rebuild_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.rebuild_server,
            'tempest.common.service_client.ServiceClient.post',
            self.FAKE_REBUILD_SERVER,
            status=202,
            server_id=self.server_id,
            image_ref='fake-image-ref'
            )

    def test_resize_server_with_str_body(self):
        self._test_resize_server()

    def test_resize_server_with_bytes_body(self):
        self._test_resize_server(True)

    def _test_resize_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.resize_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            flavor_ref='fake-flavor-ref'
            )

    def test_confirm_resize_server_with_str_body(self):
        self._test_confirm_resize_server()

    def test_confirm_resize_server_with_bytes_body(self):
        self._test_confirm_resize_server(True)

    def _test_confirm_resize_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.confirm_resize_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=204,
            server_id=self.server_id
            )

    def test_revert_resize_server_with_str_body(self):
        self._test_revert_resize()

    def test_revert_resize_server_with_bytes_body(self):
        self._test_revert_resize(True)

    def _test_revert_resize(self, bytes_body=False):
        self.check_service_client_function(
            self.client.revert_resize_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_list_server_metadata_with_str_body(self):
        self._test_list_server_metadata()

    def test_list_server_metadata_with_bytes_body(self):
        self._test_list_server_metadata()

    def _test_list_server_metadata(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_server_metadata,
            'tempest.common.service_client.ServiceClient.get',
            {'metadata': {'fake-key': 'fake-meta-data'}},
            server_id=self.server_id
            )

    def test_set_server_metadata_with_str_body(self):
        self._test_set_server_metadata()

    def test_set_server_metadata_with_bytes_body(self):
        self._test_set_server_metadata(True)

    def _test_set_server_metadata(self, bytes_body=False):
        self.check_service_client_function(
            self.client.set_server_metadata,
            'tempest.common.service_client.ServiceClient.put',
            {'metadata': {'fake-key': 'fake-meta-data'}},
            server_id=self.server_id,
            meta='fake-meta'
            )

    def test_update_server_metadata_with_str_body(self):
        self._test_update_server_metadata()

    def test_update_server_metadata_with_bytes_body(self):
        self._test_update_server_metadata(True)

    def _test_update_server_metadata(self, bytes_body=False):
        self.check_service_client_function(
            self.client.update_server_metadata,
            'tempest.common.service_client.ServiceClient.post',
            {'metadata': {'fake-key': 'fake-meta-data'}},
            server_id=self.server_id,
            meta='fake-meta'
            )

    def test_show_server_metadata_item_with_str_body(self):
        self._test_show_server_metadata()

    def test_show_server_metadata_item_with_bytes_body(self):
        self._test_show_server_metadata(True)

    def _test_show_server_metadata(self, bytes_body=False):
        self.check_service_client_function(
            self.client.show_server_metadata_item,
            'tempest.common.service_client.ServiceClient.get',
            {'meta': {'fake-key': 'fake-meta-data'}},
            server_id=self.server_id,
            key='fake-key'
            )

    def test_set_server_metadata_item_with_str_body(self):
        self._test_set_server_metadata_item()

    def test_set_server_metadata_item_with_bytes_body(self):
        self._test_set_server_metadata_item(True)

    def _test_set_server_metadata_item(self, bytes_body=False):
        self.check_service_client_function(
            self.client.set_server_metadata_item,
            'tempest.common.service_client.ServiceClient.put',
            {'meta': {'fake-key': 'fake-meta-data'}},
            server_id=self.server_id,
            key='fake-key',
            meta='fake-meta'
            )

    def test_delete_server_metadata_item_with_str_body(self):
        self._test_delete_server_metadata()

    def test_delete_server_metadata_item_with_bytes_body(self):
        self._test_delete_server_metadata(True)

    def _test_delete_server_metadata(self, bytes_body=False):
        self.check_service_client_function(
            self.client.delete_server_metadata_item,
            'tempest.common.service_client.ServiceClient.delete',
            {},
            status=204,
            server_id=self.server_id,
            key='fake-key'
            )

    def test_stop_server_with_str_body(self):
        self._test_stop_server()

    def test_stop_server_with_bytes_body(self):
        self._test_stop_server(True)

    def _test_stop_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.stop_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_start_server_with_str_body(self):
        self._test_start_server()

    def test_start_server_with_bytes_body(self):
        self._test_start_server(True)

    def _test_start_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.start_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_attach_volume_with_str_body(self):
        self._test_attach_volume_server()

    def test_attach_volume_with_bytes_body(self):
        self._test_attach_volume_server(True)

    def _test_attach_volume_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.attach_volume,
            'tempest.common.service_client.ServiceClient.post',
            {'volumeAttachment': self.FAKE_COMMON_VOLUME},
            server_id=self.server_id
            )

    def test_detach_volume_with_str_body(self):
        self._test_detach_volume_server()

    def test_detach_volume_with_bytes_body(self):
        self._test_detach_volume_server(True)

    def _test_detach_volume_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.detach_volume,
            'tempest.common.service_client.ServiceClient.delete',
            {},
            status=202,
            server_id=self.server_id,
            volume_id=self.FAKE_COMMON_VOLUME['volumeId']
            )

    def test_show_volume_attachment_with_str_body(self):
        self._test_show_volume_attachment()

    def test_show_volume_attachment_with_bytes_body(self):
        self._test_show_volume_attachment(True)

    def _test_show_volume_attachment(self, bytes_body=False):
        self.check_service_client_function(
            self.client.show_volume_attachment,
            'tempest.common.service_client.ServiceClient.get',
            {'volumeAttachment': self.FAKE_COMMON_VOLUME},
            server_id=self.server_id,
            attach_id='fake-attach-id'
            )

    def test_list_volume_attachments_with_str_body(self):
        self._test_list_volume_attachments()

    def test_list_volume_attachments_with_bytes_body(self):
        self._test_list_volume_attachments(True)

    def _test_list_volume_attachments(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_volume_attachments,
            'tempest.common.service_client.ServiceClient.get',
            {'volumeAttachments': [self.FAKE_COMMON_VOLUME]},
            server_id=self.server_id
            )

    def test_add_security_group_with_str_body(self):
        self._test_add_security_group()

    def test_add_security_group_with_bytes_body(self):
        self._test_add_security_group(True)

    def _test_add_security_group(self, bytes_body=False):
        self.check_service_client_function(
            self.client.add_security_group,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            name='fake-name'
            )

    def test_remove_security_group_with_str_body(self):
        self._test_remove_security_group()

    def test_remove_security_group_with_bytes_body(self):
        self._test_remove_security_group(True)

    def _test_remove_security_group(self, bytes_body=False):
        self.check_service_client_function(
            self.client.remove_security_group,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            name='fake-name'
            )

    def test_live_migrate_server_with_str_body(self):
        self._test_live_migrate_server()

    def test_live_migrate_server_with_bytes_body(self):
        self._test_live_migrate_server(True)

    def _test_live_migrate_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.live_migrate_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_migrate_server_with_str_body(self):
        self._test_migrate_server()

    def test_migrate_server_with_bytes_body(self):
        self._test_migrate_server(True)

    def _test_migrate_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.migrate_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_lock_server_with_str_body(self):
        self._test_lock_server()

    def test_lock_server_with_bytes_body(self):
        self._test_lock_server(True)

    def _test_lock_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.lock_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_unlock_server_with_str_body(self):
        self._test_unlock_server()

    def test_unlock_server_with_bytes_body(self):
        self._test_unlock_server(True)

    def _test_unlock_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.unlock_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_suspend_server_with_str_body(self):
        self._test_suspend_server()

    def test_suspend_server_with_bytes_body(self):
        self._test_suspend_server(True)

    def _test_suspend_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.suspend_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_resume_server_with_str_body(self):
        self._test_resume_server()

    def test_resume_server_with_bytes_body(self):
        self._test_resume_server(True)

    def _test_resume_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.resume_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_pause_server_with_str_body(self):
        self._test_pause_server()

    def test_pause_server_with_bytes_body(self):
        self._test_pause_server(True)

    def _test_pause_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.pause_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_unpause_server_with_str_body(self):
        self._test_unpause_server()

    def test_unpause_server_with_bytes_body(self):
        self._test_unpause_server(True)

    def _test_unpause_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.unpause_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_reset_state_with_str_body(self):
        self._test_reset_state()

    def test_reset_state_with_bytes_body(self):
        self._test_reset_state(True)

    def _test_reset_state(self, bytes_body=False):
        self.check_service_client_function(
            self.client.reset_state,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id,
            state='fake-state'
            )

    def test_shelve_server_with_str_body(self):
        self._test_shelve_server()

    def test_shelve_server_with_bytes_body(self):
        self._test_shelve_server(True)

    def _test_shelve_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.shelve_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_unshelve_server_with_str_body(self):
        self._test_unshelve_server()

    def test_unshelve_server_with_bytes_body(self):
        self._test_unshelve_server(True)

    def _test_unshelve_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.unshelve_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_shelve_offload_server_with_str_body(self):
        self._test_shelve_offload_server()

    def test_shelve_offload_server_with_bytes_body(self):
        self._test_shelve_offload_server(True)

    def _test_shelve_offload_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.shelve_offload_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_get_console_output_with_str_body(self):
        self._test_get_console_output()

    def test_get_console_output_with_bytes_body(self):
        self._test_get_console_output(True)

    def _test_get_console_output(self, bytes_body=False):
        self.check_service_client_function(
            self.client.get_console_output,
            'tempest.common.service_client.ServiceClient.post',
            {'output': 'fake-output'},
            server_id=self.server_id,
            length='fake-length'
            )

    def test_list_virtual_interfaces_with_str_body(self):
        self._test_list_virtual_interfaces()

    def test_list_virtual_interfaces_with_bytes_body(self):
        self._test_list_virtual_interfaces(True)

    def _test_list_virtual_interfaces(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_virtual_interfaces,
            'tempest.common.service_client.ServiceClient.get',
            {'virtual_interfaces': [self.FAKE_VIRTUAL_INTERFACES]},
            server_id=self.server_id
            )

    def test_rescue_server_with_str_body(self):
        self._test_rescue_server()

    def test_rescue_server_with_bytes_body(self):
        self._test_rescue_server(True)

    def _test_rescue_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.rescue_server,
            'tempest.common.service_client.ServiceClient.post',
            {'adminPass': 'fake-admin-pass'},
            server_id=self.server_id
            )

    def test_unrescue_server_with_str_body(self):
        self._test_unrescue_server()

    def test_unrescue_server_with_bytes_body(self):
        self._test_unrescue_server(True)

    def _test_unrescue_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.unrescue_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_show_server_diagnostics_with_str_body(self):
        self._test_show_server_diagnostics()

    def test_show_server_diagnostics_with_bytes_body(self):
        self._test_show_server_diagnostics(True)

    def _test_show_server_diagnostics(self, bytes_body=False):
        self.check_service_client_function(
            self.client.show_server_diagnostics,
            'tempest.common.service_client.ServiceClient.get',
            self.FAKE_SERVER_DIAGNOSTICS,
            status=200,
            server_id=self.server_id
            )

    def test_list_instance_actions_with_str_body(self):
        self._test_list_instance_actions()

    def test_list_instance_actions_with_bytes_body(self):
        self._test_list_instance_actions(True)

    def _test_list_instance_actions(self, bytes_body=False):
        self.check_service_client_function(
            self.client.list_instance_actions,
            'tempest.common.service_client.ServiceClient.get',
            {'instanceActions': [self.FAKE_INSTANCE_ACTIONS]},
            server_id=self.server_id
            )

    def test_show_instance_action_with_str_body(self):
        self._test_show_instance_action()

    def test_show_instance_action_with_bytes_body(self):
        self._test_show_instance_action(True)

    def _test_show_instance_action(self, bytes_body=False):
        self.check_service_client_function(
            self.client.show_instance_action,
            'tempest.common.service_client.ServiceClient.get',
            {'instanceAction': self.FAKE_INSTANCE_WITH_EVENTS},
            server_id=self.server_id,
            request_id='fake-request-id'
            )

    def test_force_delete_server_with_str_body(self):
        self._test_force_delete_server()

    def test_force_delete_server_with_bytes_body(self):
        self._test_force_delete_server(True)

    def _test_force_delete_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.force_delete_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_restore_soft_deleted_server_with_str_body(self):
        self._test_restore_soft_deleted_server()

    def test_restore_soft_deleted_server_with_bytes_body(self):
        self._test_restore_soft_deleted_server(True)

    def _test_restore_soft_deleted_server(self, bytes_body=False):
        self.check_service_client_function(
            self.client.restore_soft_deleted_server,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_reset_network_with_str_body(self):
        self._test_reset_network()

    def test_reset_network_with_bytes_body(self):
        self._test_reset_network(True)

    def _test_reset_network(self, bytes_body=False):
        self.check_service_client_function(
            self.client.reset_network,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_inject_network_info_with_str_body(self):
        self._test_inject_network_info()

    def test_inject_network_info_with_bytes_body(self):
        self._test_inject_network_info(True)

    def _test_inject_network_info(self, bytes_body=False):
        self.check_service_client_function(
            self.client.inject_network_info,
            'tempest.common.service_client.ServiceClient.post',
            {},
            status=202,
            server_id=self.server_id
            )

    def test_get_vnc_console_with_str_body(self):
        self._test_get_vnc_console()

    def test_get_vnc_console_with_bytes_body(self):
        self._test_get_vnc_console(True)

    def _test_get_vnc_console(self, bytes_body=False):
        self.check_service_client_function(
            self.client.get_vnc_console,
            'tempest.common.service_client.ServiceClient.post',
            {'console': self.FAKE_VNC_CONSOLE},
            server_id=self.server_id,
            type='fake-console-type'
            )
