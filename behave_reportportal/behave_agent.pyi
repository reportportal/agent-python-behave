from typing import Optional

from .config import Config
from reportportal_client import RPClient


def create_rp_service(cfg: Config) -> Optional[RPClient]: ...
