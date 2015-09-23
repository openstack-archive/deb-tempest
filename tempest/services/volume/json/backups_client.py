# Copyright 2014 OpenStack Foundation
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

import time

from oslo_serialization import jsonutils as json

from tempest_lib import exceptions as lib_exc

from tempest.common import service_client
from tempest import exceptions


class BaseBackupsClient(service_client.ServiceClient):
    """
    Client class to send CRUD Volume backup API requests to a Cinder endpoint
    """

    def create_backup(self, volume_id, container=None, name=None,
                      description=None):
        """Creates a backup of volume."""
        post_body = {'volume_id': volume_id}
        if container:
            post_body['container'] = container
        if name:
            post_body['name'] = name
        if description:
            post_body['description'] = description
        post_body = json.dumps({'backup': post_body})
        resp, body = self.post('backups', post_body)
        body = json.loads(body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)

    def restore_backup(self, backup_id, volume_id=None):
        """Restore volume from backup."""
        post_body = {'volume_id': volume_id}
        post_body = json.dumps({'restore': post_body})
        resp, body = self.post('backups/%s/restore' % (backup_id), post_body)
        body = json.loads(body)
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)

    def delete_backup(self, backup_id):
        """Delete a backup of volume."""
        resp, body = self.delete('backups/%s' % (str(backup_id)))
        self.expected_success(202, resp.status)
        return service_client.ResponseBody(resp, body)

    def show_backup(self, backup_id):
        """Returns the details of a single backup."""
        url = "backups/%s" % str(backup_id)
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def list_backups(self, detail=False):
        """Information for all the tenant's backups."""
        url = "backups"
        if detail:
            url += "/detail"
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def export_backup(self, backup_id):
        """Export backup metadata record."""
        url = "backups/%s/export_record" % backup_id
        resp, body = self.get(url)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def import_backup(self, backup_service, backup_url):
        """Import backup metadata record."""
        post_body = {'backup_service': backup_service,
                     'backup_url': backup_url}
        post_body = json.dumps({'backup-record': post_body})
        resp, body = self.post("backups/import_record", post_body)
        body = json.loads(body)
        self.expected_success(201, resp.status)
        return service_client.ResponseBody(resp, body)

    def wait_for_backup_status(self, backup_id, status):
        """Waits for a Backup to reach a given status."""
        body = self.show_backup(backup_id)['backup']
        backup_status = body['status']
        start = int(time.time())

        while backup_status != status:
            time.sleep(self.build_interval)
            body = self.show_backup(backup_id)['backup']
            backup_status = body['status']
            if backup_status == 'error':
                raise exceptions.VolumeBackupException(backup_id=backup_id)

            if int(time.time()) - start >= self.build_timeout:
                message = ('Volume backup %s failed to reach %s status '
                           '(current %s) within the required time (%s s).' %
                           (backup_id, status, backup_status,
                            self.build_timeout))
                raise exceptions.TimeoutException(message)

    def wait_for_backup_deletion(self, backup_id):
        """Waits for backup deletion"""
        start_time = int(time.time())
        while True:
            try:
                self.show_backup(backup_id)
            except lib_exc.NotFound:
                return
            if int(time.time()) - start_time >= self.build_timeout:
                raise exceptions.TimeoutException
            time.sleep(self.build_interval)


class BackupsClient(BaseBackupsClient):
    """Volume V1 Backups client"""
