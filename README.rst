===================
agent-python-behave
===================

.. image:: https://codecov.io/gh/reportportal/agent-python-behave/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/reportportal/agent-python-behave

Behave extension for reporting test results of Behave to the Reportal Portal.

* Usage
* Installation
* Configuration
* Launching
* Test item attributes
* Logging
* Test case ID
* Integration with GA
* Copyright Notice

Usage
-----

Installation
~~~~~~~~~~~~

To install agent-python-behave it's necessary to run :code:`pip install git+https://github.com/reportportal/agent-python-behave.git`.

You can find example of integration with behave agent `here <https://github.com/reportportal/agent-python-behave/blob/master/tests/features/environment.py>`_
You can just copy this file to your features folder.


Configuration
~~~~~~~~~~~~~

Prepare the config file :code:`behave.ini` in root directory of tests or specify
any one using behave command line option:

.. code-block:: bash

    behave -D config_file=<path_to_config_file>


The :code:`behave.ini` file should have next mandatory fields under [report_portal] section:

- :code:`token` - value could be found in the User Profile section
- :code:`project` - name of project in Report Potal
- :code:`endpoint` - address of Report Portal Server

Example of :code:`behave.ini`:

.. code-block:: text

    [report_portal]
    token = fb586627-32be-47dd-93c1-678873458a5f
    endpoint = http://192.168.1.10:8080
    project = user_personal
    launch_name = AnyLaunchName
    launch_attributes = 'Slow Smoke'
    launch_description = 'Smoke test'

The following parameters are optional:

- :code:`launch_name = AnyLaunchName` - launch name (default value is 'Python Behave Launch')
- :code:`launch_id = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` - id of the existing launch (the session will not handle the lifecycle of the given launch)
- :code:`launch_attributes = Smoke Env:Python3` - list of attributes for launch
- :code:`launch_description = Smoke test` - launch description
- :code:`step_based = True` - responsible for Scenario or Step based logging (Scenario based approach is used by default)
- :code:`is_skipped_an_issue = False` - option to mark skipped tests as not 'To Investigate' items on Server side.
- :code:`retries = 3` - amount of retries for performing REST calls to RP server
- :code:`rerun = True` - marks the launch as the rerun
- :code:`rerun_of = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`` - launch id to rerun


If you like to override the above parameters from command line, or from CI environment based on your build, then pass
- :code:`-D parameter=value` during invocation.


Launching
~~~~~~~~~
To execute tests with Report Portal you should run `behave` command and specify path to feature files:

.. code-block:: bash

    behave ./tests/features


Test item attributes
~~~~~~~~~

Tag `attribute` could be used to specify attributes for features and scenarios.
Attributes should be listed inside brackets of attribute tag separated by commas.

Example:

.. code-block:: python

    @attribute(key:value, value2)
    @attribute(some_other_attribute)
    Feature: feature name

        @attribute(key:value, value2, value3)
        Scenario: scenario name


Logging
~~~~~~~~

For logging of the test item flow to Report Portal, please, use the python
logging handler and logger class provided by extension like bellow:
in environment.py:

.. code-block:: python

    import logging

    from behave_reportportal.behave_agent import BehaveAgent, create_rp_service
    from behave_reportportal.config import read_config
    from behave_reportportal.logger import RPLogger, RPHandler


    def before_all(context):
        cfg = read_config(context)
        context.rp_agent = BehaveAgent(cfg, create_rp_service(cfg))
        context.rp_agent.start_launch(context)
        logging.setLoggerClass(RPLogger)
        log = logging.getLogger(__name__)
        log.setLevel("DEBUG")
        rph = RPHandler(rp=context.rp_agent)
        log.addHandler(rph)
        context.log = log

It's possible to send log message to launch. `is_launch_log` flag is responsible for this behaviour.
Also logger provides ability to attach some file in scope of log message (see examples below).

in steps:

.. code-block:: python

    @given("I want to calculate {number_a:d} and {number_b:d}")
    def calculate_two_numbers(context, number_a, number_b):
        context.number_a = number_a
        context.number_b = number_b
        context.log.info("log message")
        context.log.info("log message with attachment", file_to_attach="path_to_file")
        context.log.info("log message for launch", is_launch_log=True)
        context.log.info("log message for launch with attachment", file_to_attach="path_to_file", is_launch_log=True)



Test case ID
-------------------

It's possible to mark some scenario with `test_case_id(<some_id>)` tag. ID specified in brackets will be sent to ReportPortal.

Integration with GA
-------------------
ReportPortal is now supporting integrations with more than 15 test frameworks simultaneously. In order to define the most popular agents and plan the team workload accordingly, we are using Google analytics.

ReportPortal collects information about agent name and its version only. This information is sent to Google analytics on the launch start. Please help us to make our work effective.
If you still want to switch Off Google analytics, please change env variable the way below.

.. code-block:: bash

    export AGENT_NO_ANALYTICS=1


Copyright Notice
----------------
..  Copyright Notice:  https://github.com/reportportal/agent-python-behave#copyright-notice

Licensed under the `Apache 2.0`_ license (see the LICENSE file).

.. _Apache 2.0:  https://www.apache.org/licenses/LICENSE-2.0

