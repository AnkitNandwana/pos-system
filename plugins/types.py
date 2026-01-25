import strawberry
from typing import List, Optional


@strawberry.type
class Plugin:
    id: strawberry.ID
    name: str
    enabled: bool
    description: str
    config: str
    supported_events: List[str]