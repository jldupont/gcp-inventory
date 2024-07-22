"""
@author: jldupont
"""
from typing import Union
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
    """
    ProjectNumber: used along ServiceAccountEmail
                   This parameter is inspected from the target project
    """
    #
    # Used during inventory process
    #
    TargetLocations: str = field(default_factory=list)
    TargetProjectId: str = field(default="PROJECT_NOT_SET")
    TargetBucket: str = field(default_factory=str)
    TargetBucketProject: str = field(default_factory=str)

    #
    # Relevant to deployment
    #
    ProjectId: str = field(default="PROJECT_NOT_SET")
    JobRegion: str = field(default_factory=str)
    Schedule: str = field(default_factory=str)
    ProjectNumber: Union[int, None] = field(default=None)
    ServiceAccountEmail: Union[str, None] = field(default=None)

    def __post_init__(self):
        if self.Schedule is None:
            return
        if not croniter.is_valid(self.Schedule):
            raise ValueError("Invalid schedule")
