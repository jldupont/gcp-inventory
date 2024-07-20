"""
@author: jldupont
"""
from typing import List, Dict
from dataclasses import dataclass, field  # type: ignore
from croniter import croniter  # type: ignore


@dataclass
class Service:
    enabled: bool


@dataclass
class Config:
    Services: Dict[str, Service]
    JobRegion: str
    ProjectNumber: int = None
    ProjectId: str = field(default="PROJECT_NOT_SET")
    Regions: List[str] = field(default_factory=list)
    TargetBucket: str = field(default_factory=str)
    TargetBucketProject: str = field(default_factory=str)
    Schedule: str = field(default_factory=str)
    ServiceAccountEmail: str = None

    def __post_init__(self):

        if not croniter.is_valid(self.Schedule):
            raise ValueError("Invalid schedule")

        services = {
            name: Service(**attrs)
            for name, attrs in self.Services.items()
        }
        self.Services = services
