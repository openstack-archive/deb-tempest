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
from six.moves.urllib import parse as urllib
from tempest_lib.common.utils import misc
from tempest_lib import exceptions as lib_exc

from tempest.common import service_client
from tempest import exceptions


class NetworkClient(service_client.ServiceClient):

    """
    Tempest REST client for Neutron. Uses v2 of the Neutron API, since the
    V1 API has been removed from the code base.

    Implements create, delete, update, list and show for the basic Neutron
    abstractions (networks, sub-networks, routers, ports and floating IP):

    Implements add/remove interface to router using subnet ID / port ID

    It also implements list, show, update and reset for OpenStack Networking
    quotas
    """

    version = '2.0'
    uri_prefix = "v2.0"

    def _list_resources(self, uri, **filters):
        req_uri = self.uri_prefix + uri
        if filters:
            req_uri += '?' + urllib.urlencode(filters, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def _delete_resource(self, uri):
        req_uri = self.uri_prefix + uri
        resp, body = self.delete(req_uri)
        self.expected_success(204, resp.status)
        return service_client.ResponseBody(resp, body)

    def _show_resource(self, uri, **fields):
        # fields is a dict which key is 'fields' and value is a
        # list of field's name. An example:
        # {'fields': ['id', 'name']}
        req_uri = self.uri_prefix + uri
        if fields:
            req_uri += '?' + urllib.urlencode(fields, doseq=1)
        resp, body = self.get(req_uri)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def _create_resource(self, uri, post_data):
        req_uri = self.uri_prefix + uri
        req_post_data = json.dumps(post_data)
        resp, body = self.post(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(201, resp.status)
        return service_client.ResponseBody(resp, body)

    def _update_resource(self, uri, post_data):
        req_uri = self.uri_prefix + uri
        req_post_data = json.dumps(post_data)
        resp, body = self.put(req_uri, req_post_data)
        body = json.loads(body)
        self.expected_success(200, resp.status)
        return service_client.ResponseBody(resp, body)

    def create_network(self, **kwargs):
        uri = '/networks'
        post_data = {'network': kwargs}
        return self._create_resource(uri, post_data)

    def update_network(self, network_id, **kwargs):
        uri = '/networks/%s' % network_id
        post_data = {'network': kwargs}
        return self._update_resource(uri, post_data)

    def show_network(self, network_id, **fields):
        uri = '/networks/%s' % network_id
        return self._show_resource(uri, **fields)

    def delete_network(self, network_id):
        uri = '/networks/%s' % network_id
        return self._delete_resource(uri)

    def list_networks(self, **filters):
        uri = '/networks'
        return self._list_resources(uri, **filters)

    def create_subnet(self, **kwargs):
        uri = '/subnets'
        post_data = {'subnet': kwargs}
        return self._create_resource(uri, post_data)

    def update_subnet(self, subnet_id, **kwargs):
        uri = '/subnets/%s' % subnet_id
        post_data = {'subnet': kwargs}
        return self._update_resource(uri, post_data)

    def show_subnet(self, subnet_id, **fields):
        uri = '/subnets/%s' % subnet_id
        return self._show_resource(uri, **fields)

    def delete_subnet(self, subnet_id):
        uri = '/subnets/%s' % subnet_id
        return self._delete_resource(uri)

    def list_subnets(self, **filters):
        uri = '/subnets'
        return self._list_resources(uri, **filters)

    def create_port(self, **kwargs):
        uri = '/ports'
        post_data = {'port': kwargs}
        return self._create_resource(uri, post_data)

    def update_port(self, port_id, **kwargs):
        uri = '/ports/%s' % port_id
        post_data = {'port': kwargs}
        return self._update_resource(uri, post_data)

    def show_port(self, port_id, **fields):
        uri = '/ports/%s' % port_id
        return self._show_resource(uri, **fields)

    def delete_port(self, port_id):
        uri = '/ports/%s' % port_id
        return self._delete_resource(uri)

    def list_ports(self, **filters):
        uri = '/ports'
        return self._list_resources(uri, **filters)

    def create_floatingip(self, **kwargs):
        uri = '/floatingips'
        post_data = {'floatingip': kwargs}
        return self._create_resource(uri, post_data)

    def update_floatingip(self, floatingip_id, **kwargs):
        uri = '/floatingips/%s' % floatingip_id
        post_data = {'floatingip': kwargs}
        return self._update_resource(uri, post_data)

    def show_floatingip(self, floatingip_id, **fields):
        uri = '/floatingips/%s' % floatingip_id
        return self._show_resource(uri, **fields)

    def delete_floatingip(self, floatingip_id):
        uri = '/floatingips/%s' % floatingip_id
        return self._delete_resource(uri)

    def list_floatingips(self, **filters):
        uri = '/floatingips'
        return self._list_resources(uri, **filters)

    def create_metering_label(self, **kwargs):
        uri = '/metering/metering-labels'
        post_data = {'metering_label': kwargs}
        return self._create_resource(uri, post_data)

    def show_metering_label(self, metering_label_id, **fields):
        uri = '/metering/metering-labels/%s' % metering_label_id
        return self._show_resource(uri, **fields)

    def delete_metering_label(self, metering_label_id):
        uri = '/metering/metering-labels/%s' % metering_label_id
        return self._delete_resource(uri)

    def list_metering_labels(self, **filters):
        uri = '/metering/metering-labels'
        return self._list_resources(uri, **filters)

    def create_metering_label_rule(self, **kwargs):
        uri = '/metering/metering-label-rules'
        post_data = {'metering_label_rule': kwargs}
        return self._create_resource(uri, post_data)

    def show_metering_label_rule(self, metering_label_rule_id, **fields):
        uri = '/metering/metering-label-rules/%s' % metering_label_rule_id
        return self._show_resource(uri, **fields)

    def delete_metering_label_rule(self, metering_label_rule_id):
        uri = '/metering/metering-label-rules/%s' % metering_label_rule_id
        return self._delete_resource(uri)

    def list_metering_label_rules(self, **filters):
        uri = '/metering/metering-label-rules'
        return self._list_resources(uri, **filters)

    def create_security_group(self, **kwargs):
        uri = '/security-groups'
        post_data = {'security_group': kwargs}
        return self._create_resource(uri, post_data)

    def update_security_group(self, security_group_id, **kwargs):
        uri = '/security-groups/%s' % security_group_id
        post_data = {'security_group': kwargs}
        return self._update_resource(uri, post_data)

    def show_security_group(self, security_group_id, **fields):
        uri = '/security-groups/%s' % security_group_id
        return self._show_resource(uri, **fields)

    def delete_security_group(self, security_group_id):
        uri = '/security-groups/%s' % security_group_id
        return self._delete_resource(uri)

    def list_security_groups(self, **filters):
        uri = '/security-groups'
        return self._list_resources(uri, **filters)

    def create_security_group_rule(self, **kwargs):
        uri = '/security-group-rules'
        post_data = {'security_group_rule': kwargs}
        return self._create_resource(uri, post_data)

    def show_security_group_rule(self, security_group_rule_id, **fields):
        uri = '/security-group-rules/%s' % security_group_rule_id
        return self._show_resource(uri, **fields)

    def delete_security_group_rule(self, security_group_rule_id):
        uri = '/security-group-rules/%s' % security_group_rule_id
        return self._delete_resource(uri)

    def list_security_group_rules(self, **filters):
        uri = '/security-group-rules'
        return self._list_resources(uri, **filters)

    def show_extension(self, ext_alias, **fields):
        uri = '/extensions/%s' % ext_alias
        return self._show_resource(uri, **fields)

    def list_extensions(self, **filters):
        uri = '/extensions'
        return self._list_resources(uri, **filters)

    def create_bulk_network(self, names):
        network_list = [{'name': name} for name in names]
        post_data = {'networks': network_list}
        uri = '/networks'
        return self._create_resource(uri, post_data)

    def create_bulk_subnet(self, subnet_list):
        post_data = {'subnets': subnet_list}
        uri = '/subnets'
        return self._create_resource(uri, post_data)

    def create_bulk_port(self, port_list):
        post_data = {'ports': port_list}
        uri = '/ports'
        return self._create_resource(uri, post_data)

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
        except lib_exc.NotFound:
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
        message += ' (current: %s)' % resource['status']
        message += ' within the required time %s' % timeout
        caller = misc.find_test_caller()
        if caller:
            message = '(%s) %s' % (caller, message)
        raise exceptions.TimeoutException(message)

    def update_quotas(self, tenant_id, **kwargs):
        put_body = {'quota': kwargs}
        uri = '/quotas/%s' % tenant_id
        return self._update_resource(uri, put_body)

    def reset_quotas(self, tenant_id):
        uri = '/quotas/%s' % tenant_id
        return self._delete_resource(uri)

    def show_quotas(self, tenant_id, **fields):
        uri = '/quotas/%s' % tenant_id
        return self._show_resource(uri, **fields)

    def list_quotas(self, **filters):
        uri = '/quotas'
        return self._list_resources(uri, **filters)

    def create_router(self, name, admin_state_up=True, **kwargs):
        post_body = {'router': kwargs}
        post_body['router']['name'] = name
        post_body['router']['admin_state_up'] = admin_state_up
        uri = '/routers'
        return self._create_resource(uri, post_body)

    def _update_router(self, router_id, set_enable_snat, **kwargs):
        uri = '/routers/%s' % router_id
        body = self._show_resource(uri)
        update_body = {}
        update_body['name'] = kwargs.get('name', body['router']['name'])
        update_body['admin_state_up'] = kwargs.get(
            'admin_state_up', body['router']['admin_state_up'])
        cur_gw_info = body['router']['external_gateway_info']
        if cur_gw_info:
            # TODO(kevinbenton): setting the external gateway info is not
            # allowed for a regular tenant. If the ability to update is also
            # merged, a test case for this will need to be added similar to
            # the SNAT case.
            cur_gw_info.pop('external_fixed_ips', None)
            if not set_enable_snat:
                cur_gw_info.pop('enable_snat', None)
        update_body['external_gateway_info'] = kwargs.get(
            'external_gateway_info', body['router']['external_gateway_info'])
        if 'distributed' in kwargs:
            update_body['distributed'] = kwargs['distributed']
        update_body = dict(router=update_body)
        return self._update_resource(uri, update_body)

    def update_router(self, router_id, **kwargs):
        """Update a router leaving enable_snat to its default value."""
        # If external_gateway_info contains enable_snat the request will fail
        # with 404 unless executed with admin client, and therefore we instruct
        # _update_router to not set this attribute
        # NOTE(salv-orlando): The above applies as long as Neutron's default
        # policy is to restrict enable_snat usage to admins only.
        return self._update_router(router_id, set_enable_snat=False, **kwargs)

    def show_router(self, router_id, **fields):
        uri = '/routers/%s' % router_id
        return self._show_resource(uri, **fields)

    def delete_router(self, router_id):
        uri = '/routers/%s' % router_id
        return self._delete_resource(uri)

    def list_routers(self, **filters):
        uri = '/routers'
        return self._list_resources(uri, **filters)

    def update_router_with_snat_gw_info(self, router_id, **kwargs):
        """Update a router passing also the enable_snat attribute.

        This method must be execute with admin credentials, otherwise the API
        call will return a 404 error.
        """
        return self._update_router(router_id, set_enable_snat=True, **kwargs)

    def add_router_interface_with_subnet_id(self, router_id, subnet_id):
        uri = '/routers/%s/add_router_interface' % router_id
        update_body = {"subnet_id": subnet_id}
        return self._update_resource(uri, update_body)

    def add_router_interface_with_port_id(self, router_id, port_id):
        uri = '/routers/%s/add_router_interface' % router_id
        update_body = {"port_id": port_id}
        return self._update_resource(uri, update_body)

    def remove_router_interface_with_subnet_id(self, router_id, subnet_id):
        uri = '/routers/%s/remove_router_interface' % router_id
        update_body = {"subnet_id": subnet_id}
        return self._update_resource(uri, update_body)

    def remove_router_interface_with_port_id(self, router_id, port_id):
        uri = '/routers/%s/remove_router_interface' % router_id
        update_body = {"port_id": port_id}
        return self._update_resource(uri, update_body)

    def list_router_interfaces(self, uuid):
        uri = '/ports?device_id=%s' % uuid
        return self._list_resources(uri)

    def update_agent(self, agent_id, agent_info):
        """
        :param agent_info: Agent update information.
        E.g {"admin_state_up": True}
        """
        uri = '/agents/%s' % agent_id
        agent = {"agent": agent_info}
        return self._update_resource(uri, agent)

    def show_agent(self, agent_id, **fields):
        uri = '/agents/%s' % agent_id
        return self._show_resource(uri, **fields)

    def list_agents(self, **filters):
        uri = '/agents'
        return self._list_resources(uri, **filters)

    def list_routers_on_l3_agent(self, agent_id):
        uri = '/agents/%s/l3-routers' % agent_id
        return self._list_resources(uri)

    def list_l3_agents_hosting_router(self, router_id):
        uri = '/routers/%s/l3-agents' % router_id
        return self._list_resources(uri)

    def add_router_to_l3_agent(self, agent_id, router_id):
        uri = '/agents/%s/l3-routers' % agent_id
        post_body = {"router_id": router_id}
        return self._create_resource(uri, post_body)

    def remove_router_from_l3_agent(self, agent_id, router_id):
        uri = '/agents/%s/l3-routers/%s' % (agent_id, router_id)
        return self._delete_resource(uri)

    def list_dhcp_agent_hosting_network(self, network_id):
        uri = '/networks/%s/dhcp-agents' % network_id
        return self._list_resources(uri)

    def list_networks_hosted_by_one_dhcp_agent(self, agent_id):
        uri = '/agents/%s/dhcp-networks' % agent_id
        return self._list_resources(uri)

    def remove_network_from_dhcp_agent(self, agent_id, network_id):
        uri = '/agents/%s/dhcp-networks/%s' % (agent_id,
                                               network_id)
        return self._delete_resource(uri)

    def update_extra_routes(self, router_id, routes):
        uri = '/routers/%s' % router_id
        put_body = {
            'router': {
                'routes': routes
            }
        }
        return self._update_resource(uri, put_body)

    def delete_extra_routes(self, router_id):
        uri = '/routers/%s' % router_id
        put_body = {
            'router': {
                'routes': None
            }
        }
        return self._update_resource(uri, put_body)

    def add_dhcp_agent_to_network(self, agent_id, network_id):
        post_body = {'network_id': network_id}
        uri = '/agents/%s/dhcp-networks' % agent_id
        return self._create_resource(uri, post_body)
