"""
@author: jldupont
"""
from typing import List, Dict
from collections import UserList
from dataclasses import dataclass, field
from croniter import croniter


@dataclass
class Service:
    enabled: bool


@dataclass
class Config:
    Services: Dict[str, Service]
    JobRegion: str
    ProjectId: str = field(default="PROJECT_NOT_SET")
    Regions: List[str] = field(default_factory=list)
    TargetBucket: str = field(default_factory=str)
    Schedule: str = field(default_factory=str)
    ServiceAccountEmail: str = field(default=None)

    def __post_init__(self):

        if not croniter.is_valid(self.Schedule):
            raise ValueError("Invalid schedule")

        services = {
            name: Service(**attrs)
            for name, attrs in self.Services.items()
        }
        self.Services = services


class OptionalParam(UserList):
    """
    If the value resolves to None, the list resolves to empty.

    If the value resolves to something other than None,
    then the list resolves to [param, value]
    """
    def __init__(self, param, value):
        if value is None:
            super().__init__()
        else:
            super().__init__([param, value])
