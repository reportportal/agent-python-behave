from typing import Optional, Text, Dict, Any

from behave.model import Scenario
from behave.model_core import BasicStatement
from behave.runner import Context
from reportportal_client import RPClient

from .config import Config


def create_rp_service(cfg: Config) -> Optional[RPClient]: ...


class BehaveAgent:
    _rp: Optional[RPClient]
    _cfg: Config
    agent_name: Text
    agent_version: Text

    def __init__(self, cfg: Config,
                 rp_service: Optional[RPClient] = ...) -> None: ...

    def start_launch(self, context: Context, **kwargs: Any) -> None: ...

    @staticmethod
    def convert_to_rp_status(behave_status: Text) -> Text: ...

    @staticmethod
    def _code_ref(item: BasicStatement) -> Optional[Text]: ...

    @staticmethod
    def _get_parameters(scenario: Scenario) -> Optional[
        Dict[Text, Any]]: ...
