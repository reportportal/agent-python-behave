# agent-python-behave

[![PyPI version](https://img.shields.io/pypi/v/behave-reportportal.svg)](https://pypi.python.org/pypi/behave-reportportal)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/behave-reportportal.svg)](https://pypi.org/project/behave-reportportal)
[![CI](https://github.com/reportportal/agent-python-behave/actions/workflows/tests.yml/badge.svg)](https://github.com/reportportal/agent-python-behave)
[![codecov](https://codecov.io/gh/reportportal/agent-python-behave/branch/master/graph/badge.svg)](https://codecov.io/gh/reportportal/agent-python-behave)
[![Join Slack chat!](https://img.shields.io/badge/slack-join-brightgreen.svg)](https://slack.epmrpp.reportportal.io/)
[![stackoverflow](https://img.shields.io/badge/reportportal-stackoverflow-orange.svg?style=flat)](http://stackoverflow.com/questions/tagged/reportportal)

Behave extension for reporting test results of Behave to the ReportPortal.

## Usage

### Installation

To install agent-python-behave run:

```bash
pip install behave-reportportal
```

You can find an example of integration with behave
agent [here](https://github.com/reportportal/agent-python-behave/blob/master/tests/features/environment.py).
You can just copy this file to your features folder.

## Configuration

Prepare the config file `behave.ini` in the root directory of tests or specify
any one using behave command line option:

```bash
behave -D config_file=<path_to_config_file>
```

The `behave.ini` file should have the following mandatory fields under `[report_portal]` section:

- `project` - name of project in ReportPortal
- `endpoint` - address of ReportPortal Server

Example of `behave.ini`:

```text
[report_portal]
api_key = fb586627-32be-47dd-93c1-678873458a5f
endpoint = http://192.168.1.10:8080
project = user_personal
launch_name = AnyLaunchName
launch_attributes = Slow Smoke
launch_description = Smoke test
```

The following parameters are optional:

- `enabled = True` - Enable / disable ReportPortal reporting.
- `api_key` - value can be found in the User Profile section. **Required** if OAuth 2.0 is not configured.
- `oauth_uri = https://reportportal.example.com/uat/sso/oauth/token` - OAuth 2.0 token endpoint URL for password grant
  authentication. **Required** if API key is not used.
- `oauth_username = my-username` - OAuth 2.0 username for password grant authentication. **Required** if OAuth 2.0 is
  used.
- `oauth_password = my-password` - OAuth 2.0 password for password grant authentication. **Required** if OAuth 2.0 is
  used.
- `oauth_client_id = client-id` - OAuth 2.0 client identifier. **Required** if OAuth 2.0 is used.
- `oauth_client_secret = client-id-secret` - OAuth 2.0 client secret.
- `oauth_scope = offline_access` - OAuth 2.0 access token scope.
- `client_type = SYNC` - Type of the under-the-hood ReportPortal client implementation. Possible values:
  \[SYNC, ASYNC_THREAD, ASYNC_BATCHED].
- `launch_name = AnyLaunchName` - launch name (default value is 'Python Behave Launch')
- `launch_uuid = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` - UUID of the existing launch (the session will not handle the
  lifecycle of the given launch)
- `launch_attributes = Smoke Env:Python3` - list of attributes for launch
- `launch_description = Smoke test` - launch description
- `debug_mode = True` - creates the launch either as debug or default mode (defaults to False)
- `log_layout = Nested` - responsible for Scenario, Step or Nested based logging (Scenario based approach is used by
  default)
- `is_skipped_an_issue = False` - option to mark skipped tests as not 'To Investigate' items on Server side.
- `retries = 3` - amount of retries for performing REST calls to RP server
- `rerun = True` - marks the launch as the rerun
- `rerun_of = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` - launch id to rerun
- `launch_uuid_print = True` - Enables printing Launch UUID on test run start. Default `False`.
- `launch_uuid_print_output = stderr` - Launch UUID print output. Default `stdout`. Possible values: [stderr, stdout].
- `connect_timeout = 15` - Connection timeout to ReportPortal server. Default value is "10.0".
- `read_timeout = 15` - Response read timeout for ReportPortal connection. Default value is "10.0".
- `log_batch_size = 20` - maximum number of log entries which will be sent by the agent at once
- `log_batch_payload_limit = 65000000` - maximum payload size of a log batch which will be sent by the agent at once

If you would like to override the above parameters from command line, or from CI environment based on your build, then
pass:

- `-D parameter=value` during invocation.

## Launching

To execute tests with ReportPortal run `behave` command and specify path to feature files:

```bash
behave ./tests/features
```

## Test item attributes

Tag `attribute` can be used to specify attributes for features and scenarios.
Attributes should be listed inside brackets of attribute tag separated by commas.

Example:

```python
@attribute(key:value, value2)
@attribute(some_other_attribute)
Feature: feature name

    @attribute(key:value, value2, value3)
    Scenario: scenario name
```

## Logging

For logging of the test item flow to ReportPortal, please, use the python
logging handler and logger class provided by extension like below.

In `environment.py`:

```python
import logging

from reportportal_client import RPLogger, RPLogHandler

from behave_reportportal.behave_agent import BehaveAgent, create_rp_service
from behave_reportportal.config import read_config


def before_all(context):
    cfg = read_config(context)
    context.rp_client = create_rp_service(cfg)
    context.rp_client.start()
    context.rp_agent = BehaveAgent(cfg, context.rp_client)
    context.rp_agent.start_launch(context)
    logging.setLoggerClass(RPLogger)
    log = logging.getLogger(__name__)
    log.setLevel("DEBUG")
    rph = RPLogHandler(rp_client=context.rp_client)
    log.addHandler(rph)
    context.log = log
```

Logger provides ability to attach some file in scope of log message (see examples below).

In steps:

```python
@given("I want to calculate {number_a:d} and {number_b:d}")
def calculate_two_numbers(context, number_a, number_b):
    context.number_a = number_a
    context.number_b = number_b
    context.log.info("log message")

    # Message with an attachment.
    import subprocess
    free_memory = subprocess.check_output("free -h".split())
    context.log.info(
        "log message with attachment",
        attachment={
            "name": "free_memory.txt",
            "data": free_memory,
            "mime": "application/octet-stream",
        },
    )
```

## Test case ID

It's possible to mark some scenario with `test_case_id(<some_id>)` tag. ID specified in brackets will be sent to
ReportPortal.

## Integration with GA

ReportPortal is now supporting integrations with more than 15 test frameworks simultaneously. In order to define the
most popular agents and plan the team workload accordingly, we are using Google analytics.

ReportPortal collects information about agent name and its version only. This information is sent to Google analytics
on the launch start. Please help us to make our work effective. If you still want to switch Off Google analytics,
please change env variable the way below.

```bash
export AGENT_NO_ANALYTICS=1
```

## Copyright Notice

Licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license (see the LICENSE file).
