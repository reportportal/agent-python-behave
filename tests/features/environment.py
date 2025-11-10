#  Copyright (c) 2023 EPAM Systems
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License

from behave_reportportal.behave_agent import BehaveAgent
from behave_reportportal.config import read_config


def before_all(context):
    context.rp_agent = BehaveAgent(read_config(context))
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
