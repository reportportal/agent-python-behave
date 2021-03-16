===================
agent-python-behave
===================

Behave extension for reporting test results of Behave to the Reportal Portal.

* Usage
* Installation
* Configuration
* Launching
* Copyright Notice

Usage
-----

Installation
~~~~~~~~~~~~

To install agent-python-behave it's necessary to run :code:`pip install git+https://github.com/reportportal/agent-python-behave.git`.

You can find example of integration with behave agent `here <https://github.com/reportportal/agent-python-behaveblob/main/tests/features/environment.py>`_
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
- :code:`launch_attributes = 'Smoke Env:Python3'` - list of attributes for launch
- :code:`launch_description = 'Smoke test'` - launch description
- :code:`step_based = True` - responsible for Scenario or Step based logging (Scenario based approach is used by default)

If you like to override the above parameters from command line, or from CI environment based on your build, then pass
- :code:`-D parameter=value` during invocation.


Launching
~~~~~~~~~
To execute tests with Report Portal you should run `behave` command and specify path to feature files:

.. code-block:: bash

    behave ./tests/features


Copyright Notice
----------------
..  Copyright Notice:  https://github.com/reportportal/agent-python-behave#copyright-notice

Licensed under the `Apache 2.0`_ license (see the LICENSE file).

.. _Apache 2.0:  https://www.apache.org/licenses/LICENSE-2.0

