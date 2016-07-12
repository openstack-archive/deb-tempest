# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Runs tempest tests

This command is used for running the tempest tests

Test Selection
==============
Tempest run has several options:

 * **--regex/-r**: This is a selection regex like what testr uses. It will run
                   any tests that match on re.match() with the regex
 * **--smoke**: Run all the tests tagged as smoke

You can also use the **--list-tests** option in conjunction with selection
arguments to list which tests will be run.

Test Execution
==============
There are several options to control how the tests are executed. By default
tempest will run in parallel with a worker for each CPU present on the machine.
If you want to adjust the number of workers use the **--concurrency** option
and if you want to run tests serially use **--serial**

Test Output
===========
By default tempest run's output to STDOUT will be generated using the
subunit-trace output filter. But, if you would prefer a subunit v2 stream be
output to STDOUT use the **--subunit** flag

"""

import io
import os
import sys
import threading

from cliff import command
from os_testr import subunit_trace
from oslo_log import log as logging
from testrepository.commands import run_argv

from tempest import config


LOG = logging.getLogger(__name__)
CONF = config.CONF


class TempestRun(command.Command):

    def _set_env(self):
        # NOTE(mtreinish): This is needed so that testr doesn't gobble up any
        # stacktraces on failure.
        if 'TESTR_PDB' in os.environ:
            return
        else:
            os.environ["TESTR_PDB"] = ""

    def take_action(self, parsed_args):
        self._set_env()
        returncode = 0
        # Local execution mode
        if os.path.isfile('.testr.conf'):
            # If you're running in local execution mode and there is not a
            # testrepository dir create one
            if not os.path.isdir('.testrepository'):
                returncode = run_argv(['testr', 'init'], sys.stdin, sys.stdout,
                                      sys.stderr)
                if returncode:
                    sys.exit(returncode)
        else:
            print("No .testr.conf file was found for local execution")
            sys.exit(2)

        regex = self._build_regex(parsed_args)
        if parsed_args.list_tests:
            argv = ['tempest', 'list-tests', regex]
            returncode = run_argv(argv, sys.stdin, sys.stdout, sys.stderr)
        else:
            options = self._build_options(parsed_args)
            returncode = self._run(regex, options)
        sys.exit(returncode)

    def get_description(self):
        return 'Run tempest'

    def get_parser(self, prog_name):
        parser = super(TempestRun, self).get_parser(prog_name)
        parser = self._add_args(parser)
        return parser

    def _add_args(self, parser):
        # test selection args
        regex = parser.add_mutually_exclusive_group()
        regex.add_argument('--smoke', action='store_true',
                           help="Run the smoke tests only")
        regex.add_argument('--regex', '-r', default='',
                           help='A normal testr selection regex used to '
                                'specify a subset of tests to run')
        # list only args
        parser.add_argument('--list-tests', '-l', action='store_true',
                            help='List tests',
                            default=False)
        # exectution args
        parser.add_argument('--concurrency', '-w',
                            help="The number of workers to use, defaults to "
                                 "the number of cpus")
        parallel = parser.add_mutually_exclusive_group()
        parallel.add_argument('--parallel', dest='parallel',
                              action='store_true',
                              help='Run tests in parallel (this is the'
                                   ' default)')
        parallel.add_argument('--serial', dest='parallel',
                              action='store_false',
                              help='Run tests serially')
        # output args
        parser.add_argument("--subunit", action='store_true',
                            help='Enable subunit v2 output')

        parser.set_defaults(parallel=True)
        return parser

    def _build_regex(self, parsed_args):
        regex = ''
        if parsed_args.smoke:
            regex = 'smoke'
        elif parsed_args.regex:
            regex = parsed_args.regex
        return regex

    def _build_options(self, parsed_args):
        options = []
        if parsed_args.subunit:
            options.append("--subunit")
        if parsed_args.parallel:
            options.append("--parallel")
        if parsed_args.concurrency:
            options.append("--concurrency=%s" % parsed_args.concurrency)
        return options

    def _run(self, regex, options):
        returncode = 0
        argv = ['tempest', 'run', regex] + options
        if '--subunit' in options:
            returncode = run_argv(argv, sys.stdin, sys.stdout, sys.stderr)
        else:
            argv.append('--subunit')
            stdin = io.StringIO()
            stdout_r, stdout_w = os.pipe()
            subunit_w = os.fdopen(stdout_w, 'wt')
            subunit_r = os.fdopen(stdout_r)
            returncodes = {}

            def run_argv_thread():
                returncodes['testr'] = run_argv(argv, stdin, subunit_w,
                                                sys.stderr)
                subunit_w.close()

            run_thread = threading.Thread(target=run_argv_thread)
            run_thread.start()
            returncodes['subunit-trace'] = subunit_trace.trace(subunit_r,
                                                               sys.stdout)
            run_thread.join()
            subunit_r.close()
            # python version of pipefail
            if returncodes['testr']:
                returncode = returncodes['testr']
            elif returncodes['subunit-trace']:
                returncode = returncodes['subunit-trace']
        return returncode
