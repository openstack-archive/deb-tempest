# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import shutil
import subprocess
import sys

from cliff import command
from oslo_log import log as logging
from six import moves

LOG = logging.getLogger(__name__)

TESTR_CONF = """[DEFAULT]
test_command=OS_STDOUT_CAPTURE=${OS_STDOUT_CAPTURE:-1} \\
    OS_STDERR_CAPTURE=${OS_STDERR_CAPTURE:-1} \\
    OS_TEST_TIMEOUT=${OS_TEST_TIMEOUT:-500} \\
    ${PYTHON:-python} -m subunit.run discover -t %s %s $LISTOPT $IDOPTION
test_id_option=--load-list $IDFILE
test_list_option=--list
group_regex=([^\.]*\.)*
"""


def get_tempest_default_config_dir():
    """Returns the correct default config dir to support both cases of
    tempest being or not installed in a virtualenv.
    Cases considered:
    - no virtual env, python2: real_prefix and base_prefix not set
    - no virtual env, python3: real_prefix not set, base_prefix set and
      identical to prefix
    - virtualenv, python2: real_prefix and prefix are set and different
    - virtualenv, python3: real_prefix not set, base_prefix and prefix are
      set and identical
    - pyvenv, any python version: real_prefix not set, base_prefix and prefix
      are set and different

    :return: default config dir
    """
    real_prefix = getattr(sys, 'real_prefix', None)
    base_prefix = getattr(sys, 'base_prefix', None)
    prefix = sys.prefix
    if real_prefix is None and base_prefix is None:
        # Not running in a virtual environnment of any kind
        return '/etc/tempest'
    elif (real_prefix is None and base_prefix is not None and
            base_prefix == prefix):
        # Probably not running in a virtual environment
        # NOTE(andreaf) we cannot distinguish this case from the case of
        # a virtual environment created with virtualenv, and running python3.
        return '/etc/tempest'
    else:
        return os.path.join(sys.prefix, 'etc/tempest')


class TempestInit(command.Command):
    """Setup a local working environment for running tempest"""

    def get_parser(self, prog_name):
        parser = super(TempestInit, self).get_parser(prog_name)
        parser.add_argument('dir', nargs='?', default=os.getcwd())
        parser.add_argument('--config-dir', '-c', default=None)
        return parser

    def generate_testr_conf(self, local_path):
        testr_conf_path = os.path.join(local_path, '.testr.conf')
        top_level_path = os.path.dirname(os.path.dirname(__file__))
        discover_path = os.path.join(top_level_path, 'test_discover')
        testr_conf = TESTR_CONF % (top_level_path, discover_path)
        with open(testr_conf_path, 'w+') as testr_conf_file:
            testr_conf_file.write(testr_conf)

    def update_local_conf(self, conf_path, lock_dir, log_dir):
        config_parse = moves.configparser.SafeConfigParser()
        config_parse.optionxform = str
        with open(conf_path, 'w+') as conf_file:
            config_parse.readfp(conf_file)
            # Set local lock_dir in tempest conf
            if not config_parse.has_section('oslo_concurrency'):
                config_parse.add_section('oslo_concurrency')
            config_parse.set('oslo_concurrency', 'lock_path', lock_dir)
            # Set local log_dir in tempest conf
            config_parse.set('DEFAULT', 'log_dir', log_dir)
            # Set default log filename to tempest.log
            config_parse.set('DEFAULT', 'log_file', 'tempest.log')

    def copy_config(self, etc_dir, config_dir):
        shutil.copytree(config_dir, etc_dir)

    def generate_sample_config(self, local_dir):
        subprocess.call(['oslo-config-generator', '--config-file',
                         'tools/config/config-generator.tempest.conf'],
                        cwd=local_dir)

    def create_working_dir(self, local_dir, config_dir):
        # Create local dir if missing
        if not os.path.isdir(local_dir):
            LOG.debug('Creating local working dir: %s' % local_dir)
            os.mkdir(local_dir)
        lock_dir = os.path.join(local_dir, 'tempest_lock')
        etc_dir = os.path.join(local_dir, 'etc')
        config_path = os.path.join(etc_dir, 'tempest.conf')
        log_dir = os.path.join(local_dir, 'logs')
        testr_dir = os.path.join(local_dir, '.testrepository')
        # Create lock dir
        if not os.path.isdir(lock_dir):
            LOG.debug('Creating lock dir: %s' % lock_dir)
            os.mkdir(lock_dir)
        # Create log dir
        if not os.path.isdir(log_dir):
            LOG.debug('Creating log dir: %s' % log_dir)
            os.mkdir(log_dir)
        # Create and copy local etc dir
        self.copy_config(etc_dir, config_dir)
        # Generate the sample config file
        self.generate_sample_config(local_dir)
        # Update local confs to reflect local paths
        self.update_local_conf(config_path, lock_dir, log_dir)
        # Generate a testr conf file
        self.generate_testr_conf(local_dir)
        # setup local testr working dir
        if not os.path.isdir(testr_dir):
            subprocess.call(['testr', 'init'], cwd=local_dir)

    def take_action(self, parsed_args):
        config_dir = parsed_args.config_dir or get_tempest_default_config_dir()
        self.create_working_dir(parsed_args.dir, config_dir)
