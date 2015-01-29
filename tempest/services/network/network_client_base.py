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
import urllib

from tempest.common.utils import misc
from tempest import config
from tempest import exceptions

CONF = config.CONF

# the following map is used to construct proper URI
# for the given neutron resource
service_resource_prefix_map = {
    'networks': '',
    'subnets': '',
    'ports': '',
    'pools': 'lb',
    'vips': 'lb',
    'health_monitors': 'lb',
    'members': 'lb',
    'ipsecpolicies': 'vpn',
    'vpnservices': 'vpn',
    'ikepolicies': 'vpn',
    'ipsecpolicies': 'vpn',
    'metering_labels': 'metering',
    'metering_label_rules': 'metering',
    'firewall_rules': 'fw',
    'firewall_policies': 'fw',
    'firewalls': 'fw'
}

# The following list represents resource names that do not require
# changing underscore to a hyphen
hyphen_exceptions = ["health_monitors", "firewall_rules", "firewall_policies"]

# map from resource name to a plural name
# needed only for those which can't be constructed as name + 's'
resource_plural_map = {
    'security_groups': 'security_groups',
    'security_group_rules': 'security_group_rules',
    'ipsecpolicy': 'ipsecpolicies',
    'ikepolicy': 'ikepolicies',
    'ipsecpolicy': 'ipsecpolicies',
    'quotas': 'quotas',
    'firewall_policy': 'firewall_policies'
}


class NetworkClientBase(object):
    def __init__(self, auth_provider):
        self.rest_client = self.get_rest_client(
            auth_provider)
        self.rest_client.service = CONF.network.catalog_type
        self.version = '2.0'
        self.uri_prefix = "v%s" % (self.version)
        self.build_timeout = CONF.network.build_timeout
        self.build_interval = CONF.network.build_interval

    def get_rest_client(self, auth_provider):
        raise NotImplementedError

    def post(self, uri, body, headers=None):
        return self.rest_client.post(uri, body, headers)

    def put(self, uri, body, headers=None):
        return self.rest_client.put(uri, body, headers)

    def get(self, uri, headers=None):
        return self.rest_client.get(uri, headers)

    def delete(self, uri, headers=None):
        return self.rest_client.delete(uri, headers)

    def deserialize_list(self, body):
        raise NotImplementedError

    def deserialize_single(self, body):
        raise NotImplementedError

    def get_uri(self, plural_name):
        # get service prefix from resource name
        service_prefix = service_resource_prefix_map.get(
            plural_name)
        if plural_name not in hyphen_exceptions:
            plural_name = plural_name.replace("_", "-")
        if service_prefix:
            uri = '%s/%s/%s' % (self.uri_prefix, service_prefix,
                                plural_name)
        else:
            uri = '%s/%s' % (self.uri_prefix, plural_name)
        return uri

    def pluralize(self, resource_name):
        # get plural from map or just add 's'
        return resource_plural_map.get(resource_name, resource_name + 's')

    def _lister(self, plural_name):
        def _list(**filters):
            uri = self.get_uri(plural_name)
            if filters:
                uri += '?' + urllib.urlencode(filters, doseq=1)
            resp, body = self.get(uri)
            result = {plural_name: self.deserialize_list(body)}
            self.rest_client.expected_success(200, resp.status)
            return resp, result

        return _list

    def _deleter(self, resource_name):
        def _delete(resource_id):
            plural = self.pluralize(resource_name)
            uri = '%s/%s' % (self.get_uri(plural), resource_id)
            resp, body = self.delete(uri)
            self.rest_client.expected_success(204, resp.status)
            return resp, body

        return _delete

    def _shower(self, resource_name):
        def _show(resource_id, **fields):
            # fields is a dict which key is 'fields' and value is a
            # list of field's name. An example:
            # {'fields': ['id', 'name']}
            plural = self.pluralize(resource_name)
            uri = '%s/%s' % (self.get_uri(plural), resource_id)
            if fields:
                uri += '?' + urllib.urlencode(fields, doseq=1)
            resp, body = self.get(uri)
            body = self.deserialize_single(body)
            self.rest_client.expected_success(200, resp.status)
            return resp, body

        return _show

    def _creater(self, resource_name):
        def _create(**kwargs):
            plural = self.pluralize(resource_name)
            uri = self.get_uri(plural)
            post_data = self.serialize({resource_name: kwargs})
            resp, body = self.post(uri, post_data)
            body = self.deserialize_single(body)
            self.rest_client.expected_success(201, resp.status)
            return resp, body

        return _create

    def _updater(self, resource_name):
        def _update(res_id, **kwargs):
            plural = self.pluralize(resource_name)
            uri = '%s/%s' % (self.get_uri(plural), res_id)
            post_data = self.serialize({resource_name: kwargs})
            resp, body = self.put(uri, post_data)
            body = self.deserialize_single(body)
            self.rest_client.expected_success(200, resp.status)
            return resp, body

        return _update

    def __getattr__(self, name):
        method_prefixes = ["list_", "delete_", "show_", "create_", "update_"]
        method_functors = [self._lister,
                           self._deleter,
                           self._shower,
                           self._creater,
                           self._updater]
        for index, prefix in enumerate(method_prefixes):
            prefix_len = len(prefix)
            if name[:prefix_len] == prefix:
                return method_functors[index](name[prefix_len:])
        raise AttributeError(name)

    # Common methods that are hard to automate
    def create_bulk_network(self, names):
        network_list = [{'name': name} for name in names]
        post_data = {'networks': network_list}
        body = self.serialize_list(post_data, "networks", "network")
        uri = self.get_uri("networks")
        resp, body = self.post(uri, body)
        body = {'networks': self.deserialize_list(body)}
        self.rest_client.expected_success(201, resp.status)
        return resp, body

    def create_bulk_subnet(self, subnet_list):
        post_data = {'subnets': subnet_list}
        body = self.serialize_list(post_data, 'subnets', 'subnet')
        uri = self.get_uri('subnets')
        resp, body = self.post(uri, body)
        body = {'subnets': self.deserialize_list(body)}
        self.rest_client.expected_success(201, resp.status)
        return resp, body

    def create_bulk_port(self, port_list):
        post_data = {'ports': port_list}
        body = self.serialize_list(post_data, 'ports', 'port')
        uri = self.get_uri('ports')
        resp, body = self.post(uri, body)
        body = {'ports': self.deserialize_list(body)}
        self.rest_client.expected_success(201, resp.status)
        return resp, body

    def wait_for_resource_deletion(self, resource_type, id):
        """Waits for a resource to be deleted."""
        start_time = int(time.time())
        while True:
            if self.is_resource_deleted(resource_type, id):
                return
            if int(time.time()) - start_time >= self.build_timeout:
                raise exceptions.TimeoutException
            time.sleep(self.build_interval)

    def is_resource_deleted(self, resource_type, id):
        method = 'show_' + resource_type
        try:
            getattr(self, method)(id)
        except AttributeError:
            raise Exception("Unknown resource type %s " % resource_type)
        except exceptions.NotFound:
            return True
        return False

    def wait_for_resource_status(self, fetch, status, interval=None,
                                 timeout=None):
        """
        @summary: Waits for a network resource to reach a status
        @param fetch: the callable to be used to query the resource status
        @type fecth: callable that takes no parameters and returns the resource
        @param status: the status that the resource has to reach
        @type status: String
        @param interval: the number of seconds to wait between each status
          query
        @type interval: Integer
        @param timeout: the maximum number of seconds to wait for the resource
          to reach the desired status
        @type timeout: Integer
        """
        if not interval:
            interval = self.build_interval
        if not timeout:
            timeout = self.build_timeout
        start_time = time.time()

        while time.time() - start_time <= timeout:
            resource = fetch()
            if resource['status'] == status:
                return
            time.sleep(interval)

        # At this point, the wait has timed out
        message = 'Resource %s' % (str(resource))
        message += ' failed to reach status %s' % status
        message += ' within the required time %s' % timeout
        caller = misc.find_test_caller()
        if caller:
            message = '(%s) %s' % (caller, message)
        raise exceptions.TimeoutException(message)
