"""
@author: jldupont
"""
from typing import List, Dict, Union
from dataclasses import dataclass, field, asdict  # type: ignore
from croniter import croniter  # type: ignore


class _Base:
    def to_dict(self):
        return asdict(self)

    def to_json(self):
        import json
        return json.dumps(self.to_dict())


@dataclass
class Service(_Base):
    enabled: bool


@dataclass
class Config(_Base):
    Services: Dict[str, Service]
    JobRegion: str
    ProjectNumber: Union[int, None] = field(default=None)
    ProjectId: str = field(default="PROJECT_NOT_SET")
    Regions: List[str] = field(default_factory=list)
    TargetBucket: str = field(default_factory=str)
    TargetBucketProject: str = field(default_factory=str)
    Schedule: str = field(default_factory=str)
    ServiceAccountEmail: Union[str, None] = field(default=None)

    def __post_init__(self):

        if not croniter.is_valid(self.Schedule):
            raise ValueError("Invalid schedule")

        services = {
            name: Service(**attrs)
            for name, attrs in self.Services.items()
        }
        self.Services = services
