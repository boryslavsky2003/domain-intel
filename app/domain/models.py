from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class Recommendation(Enum):
    BUY = auto()
    SKIP = auto()


@dataclass(frozen=True)
class DomainAvailability:
    domain: str
    available: bool
    price: Optional[float] = None
    currency: Optional[str] = None


@dataclass(frozen=True)
class DomainAppraisal:
    domain: str
    go_value: float
    sale_probability: float


@dataclass(frozen=True)
class DomainEvaluation:
    domain: str
    is_available: bool
    go_value: float
    sale_probability: float
    recommendation: Recommendation
