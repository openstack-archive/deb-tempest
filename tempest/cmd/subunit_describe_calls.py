# Copyright 2016 Rackspace
#
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
subunit-describe-calls is a parser for subunit streams to determine what REST
API calls are made inside of a test and in what order they are called.

Runtime Arguments
-----------------

**--subunit, -s**: (Required) The path to the subunit file being parsed

**--non-subunit-name, -n**: (Optional) The file_name that the logs are being
stored in

**--output-file, -o**: (Required) The path where the JSON output will be
written to

**--ports, -p**: (Optional) The path to a JSON file describing the ports being
used by different services

Usage
-----

subunit-describe-calls will take in a file path via the --subunit parameter
which contains either a subunit v1 or v2 stream. This is then parsed checking
for details contained in the file_bytes of the --non-subunit-name parameter
(the default is pythonlogging which is what Tempest uses to store logs). By
default the OpenStack Kilo release port defaults (http://bit.ly/22jpF5P)
are used unless a file is provided via the --ports option. The resulting output
is dumped in JSON output to the path provided in the --output-file option.

Ports file JSON structure
^^^^^^^^^^^^^^^^^^^^^^^^^

  {
      "<port number>": "<name of service>",
      ...
  }


Output file JSON structure
^^^^^^^^^^^^^^^^^^^^^^^^^^
  {
      "full_test_name[with_id_and_tags]": [
          {
              "name": "The ClassName.MethodName that made the call",
              "verb": "HTTP Verb",
              "service": "Name of the service",
              "url": "A shortened version of the URL called",
              "status_code": "The status code of the response"
          }
      ]
  }
"""
import argparse
import collections
import io
import json
import os
import re

import subunit
import testtools


class UrlParser(testtools.TestResult):
    uuid_re = re.compile(r'(^|[^0-9a-f])[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-'
                         '[0-9a-f]{4}-[0-9a-f]{12}([^0-9a-f]|$)')
    id_re = re.compile(r'(^|[^0-9a-z])[0-9a-z]{8}[0-9a-z]{4}[0-9a-z]{4}'
                       '[0-9a-z]{4}[0-9a-z]{12}([^0-9a-z]|$)')
    ip_re = re.compile(r'(^|[^0-9])[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]'
                       '{1,3}([^0-9]|$)')
    url_re = re.compile(r'.*INFO.*Request \((?P<name>.*)\): (?P<code>[\d]{3}) '
                        '(?P<verb>\w*) (?P<url>.*) .*')
    port_re = re.compile(r'.*:(?P<port>\d+).*')
    path_re = re.compile(r'http[s]?://[^/]*/(?P<path>.*)')

    # Based on mitaka defaults:
    # http://docs.openstack.org/mitaka/config-reference/
    # firewalls-default-ports.html
    services = {
        "8776": "Block Storage",
        "8774": "Nova",
        "8773": "Nova-API", "8775": "Nova-API",
        "8386": "Sahara",
        "35357": "Keystone", "5000": "Keystone",
        "9292": "Glance", "9191": "Glance",
        "9696": "Neutron",
        "6000": "Swift", "6001": "Swift", "6002": "Swift",
        "8004": "Heat", "8000": "Heat", "8003": "Heat",
        "8777": "Ceilometer",
        "80": "Horizon",
        "8080": "Swift",
        "443": "SSL",
        "873": "rsync",
        "3260": "iSCSI",
        "3306": "MySQL",
        "5672": "AMQP"}

    def __init__(self, services=None):
        super(UrlParser, self).__init__()
        self.test_logs = {}
        self.services = services or self.services

    def addSuccess(self, test, details=None):
        output = test.shortDescription() or test.id()
        calls = self.parse_details(details)
        self.test_logs.update({output: calls})

    def addSkip(self, test, err, details=None):
        output = test.shortDescription() or test.id()
        calls = self.parse_details(details)
        self.test_logs.update({output: calls})

    def addError(self, test, err, details=None):
        output = test.shortDescription() or test.id()
        calls = self.parse_details(details)
        self.test_logs.update({output: calls})

    def addFailure(self, test, err, details=None):
        output = test.shortDescription() or test.id()
        calls = self.parse_details(details)
        self.test_logs.update({output: calls})

    def stopTestRun(self):
        super(UrlParser, self).stopTestRun()

    def startTestRun(self):
        super(UrlParser, self).startTestRun()

    def parse_details(self, details):
        if details is None:
            return

        calls = []
        for _, detail in details.items():
            for line in detail.as_text().split("\n"):
                match = self.url_re.match(line)
                if match is not None:
                    calls.append({
                        "name": match.group("name"),
                        "verb": match.group("verb"),
                        "status_code": match.group("code"),
                        "service": self.get_service(match.group("url")),
                        "url": self.url_path(match.group("url"))})

        return calls

    def get_service(self, url):
        match = self.port_re.match(url)
        if match is not None:
            return self.services.get(match.group("port"), "Unknown")
        return "Unknown"

    def url_path(self, url):
        match = self.path_re.match(url)
        if match is not None:
            path = match.group("path")
            path = self.uuid_re.sub(r'\1<uuid>\2', path)
            path = self.ip_re.sub(r'\1<ip>\2', path)
            path = self.id_re.sub(r'\1<id>\2', path)
            return path
        return url


class FileAccumulator(testtools.StreamResult):

    def __init__(self, non_subunit_name='pythonlogging'):
        super(FileAccumulator, self).__init__()
        self.route_codes = collections.defaultdict(io.BytesIO)
        self.non_subunit_name = non_subunit_name

    def status(self, **kwargs):
        if kwargs.get('file_name') != self.non_subunit_name:
            return
        file_bytes = kwargs.get('file_bytes')
        if not file_bytes:
            return
        route_code = kwargs.get('route_code')
        stream = self.route_codes[route_code]
        stream.write(file_bytes)


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        desc = "Outputs all HTTP calls a given test made that were logged."
        super(ArgumentParser, self).__init__(description=desc)

        self.prog = "Argument Parser"

        self.add_argument(
            "-s", "--subunit", metavar="<subunit file>", required=True,
            default=None, help="The path to the subunit output file.")

        self.add_argument(
            "-n", "--non-subunit-name", metavar="<non subunit name>",
            default="pythonlogging",
            help="The name used in subunit to describe the file contents.")

        self.add_argument(
            "-o", "--output-file", metavar="<output file>", default=None,
            help="The output file name for the json.", required=True)

        self.add_argument(
            "-p", "--ports", metavar="<ports file>", default=None,
            help="A JSON file describing the ports for each service.")


def parse(subunit_file, non_subunit_name, ports):
    if ports is not None and os.path.exists(ports):
        ports = json.loads(open(ports).read())

    url_parser = UrlParser(ports)
    stream = open(subunit_file, 'rb')
    suite = subunit.ByteStreamToStreamResult(
        stream, non_subunit_name=non_subunit_name)
    result = testtools.StreamToExtendedDecorator(url_parser)
    accumulator = FileAccumulator(non_subunit_name)
    result = testtools.StreamResultRouter(result)
    result.add_rule(accumulator, 'test_id', test_id=None)
    result.startTestRun()
    suite.run(result)

    for bytes_io in accumulator.route_codes.values():  # v1 processing
        bytes_io.seek(0)
        suite = subunit.ProtocolTestCase(bytes_io)
        suite.run(url_parser)
    result.stopTestRun()

    return url_parser


def output(url_parser, output_file):
    with open(output_file, "w") as outfile:
        outfile.write(json.dumps(url_parser.test_logs))


def entry_point():
    cl_args = ArgumentParser().parse_args()
    parser = parse(cl_args.subunit, cl_args.non_subunit_name, cl_args.ports)
    output(parser, cl_args.output_file)


if __name__ == "__main__":
    entry_point()
