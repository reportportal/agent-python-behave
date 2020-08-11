from mss import mss     # Takes a screenshot of monitor
from features.lib.helpers.rp_driver import (start_launcher, start_feature_test, timestamp, start_scenario_test,
                                            log_step_result, finish_launcher, terminate_service,
                                            finish_scenario_test, finish_feature, start_step_test, finish_step_test)


def before_all(context):
    context.rp_enable = context.config.userdata.getbool('rp_enable', True)
    context.step_based = context.config.userdata.getbool('step_based', False)
    #   Starts Launcher
    start_launcher(name='Step based run' if context.step_based else 'Scenario based run',
                   start_time=timestamp(), tags=context.config.tags.ands[0],
                   description='Your launcher description here')


def before_feature(context, feature):
    #   Starts Feature
    if context.rp_enable:
        start_feature_test(name='Feature: %s' % feature.name,
                           description='Feature description:\n%s' % '\n'.join(feature.description),
                           tags=feature.tags,
                           start_time=timestamp(),
                           item_type='SUITE')


def before_scenario(context, scenario):
    #   Starts scenario test item.
    if context.rp_enable:
        start_scenario_test(name='Scenario: %s' % scenario.name, description='Your scenario description',
                            tags=scenario.tags, start_time=timestamp(), item_type='SCENARIO')


# This method executed in case when context.step_based ir True
def before_step(context, step):
    if context.rp_enable and context.step_based:
        description = None
        if step.table:
            table_data = []
            for row in step.table.rows:
                table_data.append('|'.join(row))
            description = "|%s|" % '|\n|'.join(table_data)
        elif step.text:
            # Logs step with text if it was provided
            description = step.text

        start_step_test(name='%s %s' % (step.keyword, step.name), start_time=timestamp(), item_type='STEP',
                        description=description if description is not None else None)


def after_step(context, step):
    # If step_based parameter is True then STEP based logging will be used
    if context.rp_enable and context.step_based:
        # Finishes step
        if step.status == 'failed':
            # Takes a demo screenshot of desktop (can be removed)
            with mss() as sct:
                screenshot_name = sct.shot()

            # Logs assertion message with attachment and ERROR level it step was failed.
            log_step_result(end_time=timestamp(), message=step.exception.message, level='ERROR',
                            attachment={
                                'name': 'failed_scenario_name',
                                # 'data': context.driver.get_screenshot_as_png(), can be used for selenium
                                'data': open(screenshot_name, 'rb'),
                                'mime': 'application/octet-stream'
                            }
                            )

            finish_step_test(end_time=timestamp(), status='FAILED')
        else:
            finish_step_test(end_time=timestamp(), status='PASSED')

    # Else SCENARIO based logging will be used
    elif context.rp_enable:
        # Creates text log message with INFO level.
        if step.table:
            # Logs step with data table if it was provided
            table_data = []
            for row in step.table.rows:
                table_data.append('|'.join(row))
            table_result = "|%s|" % '|\n|'.join(table_data)
            log_step_result(end_time=timestamp(),
                            message='%s %s\n~~~~~~~~~~~~~~~~~~~~~~~~~\nStep data table:\n%s' % (step.keyword,
                                                                                                step.name,
                                                                                                table_result),
                            level='INFO')
        elif step.text:
            # Logs step with text if it was provided
            log_step_result(end_time=timestamp(),
                            message='%s %s\n~~~~~~~~~~~~~~~~~~~~~~~~~\nStep data text:\n%s' % (step.keyword,
                                                                                               step.name,
                                                                                               step.text),
                            level='INFO')
        else:
            # Logs step name if it is passed
            log_step_result(end_time=timestamp(), message='%s %s' % (step.keyword, step.name), level='INFO')

        if step.status == 'failed':
            # Takes a demo screenshot of desktop (can be removed)
            with mss() as sct:
                screenshot_name = sct.shot()

            # Logs assertion message with attachment and ERROR level it step was failed.
            log_step_result(end_time=timestamp(), message=step.exception.message, level='ERROR',
                            attachment={
                                'name': 'failed_scenario_name',
                                # 'data': context.driver.get_screenshot_as_png(), can be used for selenium
                                'data': open(screenshot_name, 'rb'),
                                'mime': 'application/octet-stream'
                            }
                            )


def after_scenario(context, scenario):
    if context.rp_enable:
        for step in scenario.steps:
            if step.status.name == 'undefined':
                # Logs scenario if it is undefined
                log_step_result(end_time=timestamp(),
                                message='%s %s - step is undefined.\nPlease define step.' % (step.keyword, step.name),
                                level='WARN')
                # Logs scenario as skipped if it is marked for skip
                # For example scenario marked by @skip tag and --tags=~@skip specified in params of run
            elif step.status.name == 'skipped':
                log_step_result(end_time=timestamp(),
                                message='%s %s - %s' % (step.keyword, step.name, step.status.name.capitalize()),
                                level='TRACE')
        #   Finishes scenario
        if scenario.status == 'failed':
            finish_scenario_test(end_time=timestamp(), status='FAILED')
        else:
            finish_scenario_test(end_time=timestamp(), status='PASSED')


def after_feature(context, feature):
    if context.rp_enable:
        for i in feature.scenarios:
            try:
                if i.tags[0] == 'skip':
                    start_scenario_test(name='Scenario: %s' % i.name,
                                        description=i.description[0],
                                        tags=feature.tags, start_time=timestamp(), item_type='SCENARIO')
                    finish_scenario_test(end_time=timestamp(), status='SKIPPED')
            except IndexError:
                pass
        #   Finishes feature
        finish_feature(end_time=timestamp(), status='FAILED') if feature.status == 'failed' else finish_feature(
            end_time=timestamp(), status='PASSED')


def after_all(context):
    #   Finishes the launcher and terminates the service.
    if context.rp_enable:
        finish_launcher(end_time=timestamp())
        terminate_service()
