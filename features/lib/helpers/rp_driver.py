import ConfigParser
import os
import traceback

from reportportal_client import ReportPortalServiceAsync
from time import time

rp_config = ConfigParser.SafeConfigParser()
config_path = os.path.join('behave.local.ini')
if not os.path.exists(config_path):
    config_path = os.path.join('behave.ini')
rp_config.read(config_path)

rp_endpoint = rp_config.get('report_portal', 'rp_endpoint')
rp_project = rp_config.get('report_portal', 'rp_project')
rp_token = rp_config.get('report_portal', 'rp_token')
rp_launch_name = rp_config.get('report_portal', 'rp_launch_name')
rp_launch_description = rp_config.get('report_portal', 'rp_launch_description')


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    print("Error occurred: {}".format(exc_info[1]))
    traceback.print_exception(*exc_info)


def timestamp():
    return str(int(time() * 1000))


service = ReportPortalServiceAsync(endpoint=rp_endpoint, project=rp_project,
                                   token=rp_token, error_handler=my_error_handler)
# Disables SSL verification
# service.rp_client.session.verify = False


def start_launcher(name, start_time, description=None, tags=None):
    service.start_launch(name=name, start_time=start_time, description=description, tags=tags)


def start_feature_test(**kwargs):
    start_test(**kwargs)


def start_scenario_test(**kwargs):
    return start_test(**kwargs)


def start_step_test(**kwargs):
    return start_test(**kwargs)


def finish_step_test(**kwargs):
    return finish_test(**kwargs)


def finish_scenario_test(**kwargs):
    return finish_test(**kwargs)


def start_test(name, start_time, item_type, description=None, tags=None):
    """
    item_type can be (SUITE, STORY, TEST, SCENARIO, STEP, BEFORE_CLASS,
    BEFORE_GROUPS, BEFORE_METHOD, BEFORE_SUITE, BEFORE_TEST, AFTER_CLASS,
    AFTER_GROUPS, AFTER_METHOD, AFTER_SUITE, AFTER_TEST)
    Types taken from report_portal/service.py
    """
    service.start_test_item(name=name, description=description, tags=tags, start_time=start_time, item_type=item_type)


def finish_test(end_time, status, issue=None):
    service.finish_test_item(end_time=end_time, status=status, issue=issue)


def log_step_result(end_time, message, level='INFO', attachment=None):
    service.log(time=end_time, message=message, level=level, attachment=attachment)


def finish_feature(end_time, status, issue=None):
    """
    status can be (untested, skipped, passed, failed, undefined, executing)
    """
    service.finish_test_item(end_time=end_time, status=status, issue=issue)


def finish_launcher(end_time, status=None):
    service.finish_launch(end_time=end_time, status=status)


def terminate_service():
    service.terminate()

