# Copyright 2013 OpenStack Foundation
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

from lxml import etree

from tempest.common import http
from tempest.common import rest_client
from tempest.common import xml_utils as common
from tempest import config

CONF = config.CONF

XMLNS = "http://docs.openstack.org/identity/api/v3"


class PolicyClientXML(rest_client.RestClient):
    TYPE = "xml"

    def __init__(self, auth_provider):
        super(PolicyClientXML, self).__init__(auth_provider)
        self.service = CONF.identity.catalog_type
        self.endpoint_url = 'adminURL'
        self.api_version = "v3"

    def _parse_array(self, node):
        array = []
        for child in node.getchildren():
            tag_list = child.tag.split('}', 1)
            if tag_list[1] == "policy":
                array.append(common.xml_to_json(child))
        return array

    def _parse_body(self, body):
        json = common.xml_to_json(body)
        return json

    def request(self, method, url, extra_headers=False, headers=None,
                body=None, wait=None):
        """Overriding the existing HTTP request in super class RestClient."""
        if extra_headers:
            try:
                headers.update(self.get_headers())
            except (ValueError, TypeError):
                headers = self.get_headers()
        dscv = CONF.identity.disable_ssl_certificate_validation
        self.http_obj = http.ClosingHttp(
            disable_ssl_certificate_validation=dscv)
        return super(PolicyClientXML, self).request(method, url,
                                                    extra_headers,
                                                    headers=headers,
                                                    body=body)

    def create_policy(self, blob, type):
        """Creates a Policy."""
        create_policy = common.Element("policy", xmlns=XMLNS,
                                       blob=blob, type=type)
        resp, body = self.post('policies', str(common.Document(create_policy)))
        self.expected_success(201, resp.status)
        body = self._parse_body(etree.fromstring(body))
        return resp, body

    def list_policies(self):
        """Lists the policies."""
        resp, body = self.get('policies')
        self.expected_success(200, resp.status)
        body = self._parse_array(etree.fromstring(body))
        return resp, body

    def get_policy(self, policy_id):
        """Lists out the given policy."""
        url = 'policies/%s' % policy_id
        resp, body = self.get(url)
        self.expected_success(200, resp.status)
        body = self._parse_body(etree.fromstring(body))
        return resp, body

    def update_policy(self, policy_id, **kwargs):
        """Updates a policy."""
        type = kwargs.get('type')
        update_policy = common.Element("policy", xmlns=XMLNS, type=type)
        url = 'policies/%s' % policy_id
        resp, body = self.patch(url, str(common.Document(update_policy)))
        self.expected_success(200, resp.status)
        body = self._parse_body(etree.fromstring(body))
        return resp, body

    def delete_policy(self, policy_id):
        """Deletes the policy."""
        url = "policies/%s" % policy_id
        resp, body = self.delete(url)
        self.expected_success(204, resp.status)
        return resp, body
