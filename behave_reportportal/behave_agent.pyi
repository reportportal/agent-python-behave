from typing import Optional, Text, Dict, Any, List, Union

from behave.model import Scenario, Feature
from behave.model_core import BasicStatement, TagAndStatusStatement, \
    TagStatement
from behave.runner import Context
from reportportal_client import RPClient

from .config import Config


def create_rp_service(cfg: Config) -> Optional[RPClient]: ...


class BehaveAgent:
    _rp: Optional[RPClient]
    _cfg: Config
    _handle_lifecycle: bool
    agent_name: Text
    agent_version: Text

    def __init__(self, cfg: Config,
                 rp_service: Optional[RPClient] = ...) -> None: ...

    def start_launch(self, context: Context, **kwargs: Any) -> None: ...

    def _get_launch_attributes(self) -> List[Dict[Text, Text]]: ...

    def _attributes(self, item: Union[TagAndStatusStatement,
    TagStatement]) -> List[Dict[Text, Text]]: ...

    def finish_launch(self, context: Context, **kwargs) -> None: ...

    @staticmethod
    def _get_attributes_from_tags(tags: List[Text]) -> List[Text]: ...

    @staticmethod
    def _test_case_id(scenario: Scenario) -> Text: ...

    @staticmethod
    def _item_description(item: Union[Scenario, Feature]) -> Text: ...

    @staticmethod
    def convert_to_rp_status(behave_status: Text) -> Text: ...

    @staticmethod
    def _code_ref(item: BasicStatement) -> Optional[Text]: ...

    @staticmethod
    def _get_parameters(scenario: Scenario) -> Optional[
        Dict[Text, Any]]: ...
