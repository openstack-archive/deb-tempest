# Copyright 2013 Hewlett-Packard, Ltd.
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


import json
import re
import string
import unicodedata

import testscenarios
import testtools

from tempest import auth
from tempest import clients
from tempest.common.utils import misc
from tempest import config

CONF = config.CONF


@misc.singleton
class ImageUtils(object):

    default_ssh_user = 'root'

    def __init__(self):
        # Load configuration items
        self.ssh_users = json.loads(CONF.input_scenario.ssh_user_regex)
        self.non_ssh_image_pattern = \
            CONF.input_scenario.non_ssh_image_regex
        # Setup clients
        os = clients.Manager()
        self.images_client = os.images_client
        self.flavors_client = os.flavors_client

    def ssh_user(self, image_id):
        _, _image = self.images_client.get_image(image_id)
        for regex, user in self.ssh_users:
            # First match wins
            if re.match(regex, _image['name']) is not None:
                return user
        else:
            return self.default_ssh_user

    def _is_sshable_image(self, image):
        return not re.search(pattern=self.non_ssh_image_pattern,
                             string=str(image['name']))

    def is_sshable_image(self, image_id):
        _, _image = self.images_client.get_image(image_id)
        return self._is_sshable_image(_image)

    def _is_flavor_enough(self, flavor, image):
        return image['minDisk'] <= flavor['disk']

    def is_flavor_enough(self, flavor_id, image_id):
        _, _image = self.images_client.get_image(image_id)
        _, _flavor = self.flavors_client.get_flavor_details(flavor_id)
        return self._is_flavor_enough(_flavor, _image)


@misc.singleton
class InputScenarioUtils(object):

    """
    Example usage:

    import testscenarios
    (...)
    load_tests = testscenarios.load_tests_apply_scenarios


    class TestInputScenario(manager.ScenarioTest):

        scenario_utils = utils.InputScenarioUtils()
        scenario_flavor = scenario_utils.scenario_flavors
        scenario_image = scenario_utils.scenario_images
        scenarios = testscenarios.multiply_scenarios(scenario_image,
                                                     scenario_flavor)

        def test_create_server_metadata(self):
            name = rand_name('instance')
            self.servers_client.create_server(name=name,
                                              flavor_ref=self.flavor_ref,
                                              image_ref=self.image_ref)
    """
    validchars = "-_.{ascii}{digit}".format(ascii=string.ascii_letters,
                                            digit=string.digits)

    def __init__(self):
        os = clients.Manager(
            auth.get_default_credentials('user', fill_in=False))
        self.images_client = os.images_client
        self.flavors_client = os.flavors_client
        self.image_pattern = CONF.input_scenario.image_regex
        self.flavor_pattern = CONF.input_scenario.flavor_regex

    def _normalize_name(self, name):
        nname = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
        nname = ''.join(c for c in nname if c in self.validchars)
        return nname

    @property
    def scenario_images(self):
        """
        :return: a scenario with name and uuid of images
        """
        if not CONF.service_available.glance:
            return []
        if not hasattr(self, '_scenario_images'):
            _, images = self.images_client.list_images()
            self._scenario_images = [
                (self._normalize_name(i['name']), dict(image_ref=i['id']))
                for i in images if re.search(self.image_pattern,
                                             str(i['name']))
            ]
        return self._scenario_images

    @property
    def scenario_flavors(self):
        """
        :return: a scenario with name and uuid of flavors
        """
        if not hasattr(self, '_scenario_flavors'):
            _, flavors = self.flavors_client.list_flavors()
            self._scenario_flavors = [
                (self._normalize_name(f['name']), dict(flavor_ref=f['id']))
                for f in flavors if re.search(self.flavor_pattern,
                                              str(f['name']))
            ]
        return self._scenario_flavors


def load_tests_input_scenario_utils(*args):
    """
    Wrapper for testscenarios to set the scenarios to avoid running a getattr
    on the CONF object at import.
    """
    if getattr(args[0], 'suiteClass', None) is not None:
        loader, standard_tests, pattern = args
    else:
        standard_tests, module, loader = args
    scenario_utils = InputScenarioUtils()
    scenario_flavor = scenario_utils.scenario_flavors
    scenario_image = scenario_utils.scenario_images
    for test in testtools.iterate_tests(standard_tests):
        setattr(test, 'scenarios', testscenarios.multiply_scenarios(
            scenario_image,
            scenario_flavor))
    return testscenarios.load_tests_apply_scenarios(*args)
