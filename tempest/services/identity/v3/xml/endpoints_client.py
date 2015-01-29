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


class EndPointClientXML(rest_client.RestClient):
    TYPE = "xml"

    def __init__(self, auth_provider):
        super(EndPointClientXML, self).__init__(auth_provider)
        self.service = CONF.identity.catalog_type
        self.endpoint_url = 'adminURL'
        self.api_version = "v3"

    def _parse_array(self, node):
        array = []
        for child in node.getchildren():
            tag_list = child.tag.split('}', 1)
            if tag_list[1] == "endpoint":
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
        return super(EndPointClientXML, self).request(method, url,
                                                      extra_headers,
                                                      headers=headers,
                                                      body=body)

    def list_endpoints(self):
        """Get the list of endpoints."""
        resp, body = self.get("endpoints")
        self.expected_success(200, resp.status)
        body = self._parse_array(etree.fromstring(body))
        return resp, body

    def create_endpoint(self, service_id, interface, url, **kwargs):
        """Create endpoint.

        Normally this function wouldn't allow setting values that are not
        allowed for 'enabled'. Use `force_enabled` to set a non-boolean.

        """
        region = kwargs.get('region', None)
        if 'force_enabled' in kwargs:
            enabled = kwargs['force_enabled']
        else:
            enabled = kwargs.get('enabled', None)
            if enabled is not None:
                enabled = str(enabled).lower()
        create_endpoint = common.Element("endpoint",
                                         xmlns=XMLNS,
                                         service_id=service_id,
                                         interface=interface,
                                         url=url, region=region,
                                         enabled=enabled)
        resp, body = self.post('endpoints',
                               str(common.Document(create_endpoint)))
        self.expected_success(201, resp.status)
        body = self._parse_body(etree.fromstring(body))
        return resp, body

    def update_endpoint(self, endpoint_id, service_id=None, interface=None,
                        url=None, region=None, enabled=None, **kwargs):
        """Updates an endpoint with given parameters.

        Normally this function wouldn't allow setting values that are not
        allowed for 'enabled'. Use `force_enabled` to set a non-boolean.

        """
        doc = common.Document()
        endpoint = common.Element("endpoint")
        doc.append(endpoint)

        if service_id:
            endpoint.add_attr("service_id", service_id)
        if interface:
            endpoint.add_attr("interface", interface)
        if url:
            endpoint.add_attr("url", url)
        if region:
            endpoint.add_attr("region", region)

        if 'force_enabled' in kwargs:
            endpoint.add_attr("enabled", kwargs['force_enabled'])
        elif enabled is not None:
            endpoint.add_attr("enabled", str(enabled).lower())

        resp, body = self.patch('endpoints/%s' % str(endpoint_id), str(doc))
        self.expected_success(200, resp.status)
        body = self._parse_body(etree.fromstring(body))
        return resp, body

    def delete_endpoint(self, endpoint_id):
        """Delete endpoint."""
        resp_header, resp_body = self.delete('endpoints/%s' % endpoint_id)
        self.expected_success(204, resp_header.status)
        return resp_header, resp_body
