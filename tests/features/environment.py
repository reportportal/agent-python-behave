from behave_reportportal.behave_agent import BehaveAgent, create_rp_service
from behave_reportportal.config import read_config


cfg = None
rp_agent = None


def before_all(context):
    global cfg, rp_agent
    cfg = read_config(context)
    rp_agent = BehaveAgent(cfg, create_rp_service(cfg))
    rp_agent.start_launch(context)


def after_all(context):
    if rp_agent:
        rp_agent.finish_launch(context)


def before_feature(context, feature):
    if rp_agent:
        rp_agent.start_feature(context, feature)


def after_feature(context, feature):
    if rp_agent:
        rp_agent.finish_feature(context, feature)


def before_scenario(context, scenario):
    if rp_agent:
        rp_agent.start_scenario(context, scenario)


def after_scenario(context, scenario):
    if rp_agent:
        rp_agent.finish_scenario(context, scenario)


def before_step(context, step):
    if rp_agent:
        rp_agent.start_step(context, step)


def after_step(context, step):
    if rp_agent:
        rp_agent.finish_step(context, step)
