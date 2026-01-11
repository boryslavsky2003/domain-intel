from abc import ABC, abstractmethod
from app.domain.models import DomainAvailability, DomainAppraisal


class AvailabilityProvider(ABC):
    @abstractmethod
    def check_availability(self, domain: str) -> DomainAvailability:
        pass


class AppraisalProvider(ABC):
    @abstractmethod
    def get_appraisal(self, domain: str) -> DomainAppraisal:
        pass


class WhoisProvider(ABC):
    @abstractmethod
    def get_registrant(self, domain: str) -> str:
        pass
