from behave_reportportal.behave_agent import BehaveAgent, create_rp_service
from behave_reportportal.config import read_config


def before_all(context):
    cfg = read_config(context)
    context.rp_agent = BehaveAgent(cfg, create_rp_service(cfg))
    context.rp_agent.start_launch(context)


def after_all(context):
    context.rp_agent.finish_launch(context)


def before_feature(context, feature):
    context.rp_agent.start_feature(context, feature)


def after_feature(context, feature):
    context.rp_agent.finish_feature(context, feature)


def before_scenario(context, scenario):
    context.rp_agent.start_scenario(context, scenario)


def after_scenario(context, scenario):
    context.rp_agent.finish_scenario(context, scenario)


def before_step(context, step):
    context.rp_agent.start_step(context, step)


def after_step(context, step):
    context.rp_agent.finish_step(context, step)
