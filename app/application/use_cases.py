from typing import List
from app.domain.models import (
    DomainEvaluation,
    Recommendation,
    DomainAvailability,
    DomainAppraisal,
)
from app.domain.ports import AvailabilityProvider, AppraisalProvider, WhoisProvider


class EvaluateDomainUseCase:
    def __init__(
        self,
        availability_provider: AvailabilityProvider,
        appraisal_provider: AppraisalProvider,
        whois_provider: WhoisProvider,
    ):
        self._availability_provider = availability_provider
        self._appraisal_provider = appraisal_provider
        self._whois_provider = whois_provider

    def execute(self, domain: str) -> DomainEvaluation:
        # Arthur's logic: Check availability first
        availability: DomainAvailability = (
            self._availability_provider.check_availability(domain)
        )

        # Get appraisal to combine results as per requirements
        appraisal: DomainAppraisal = self._appraisal_provider.get_appraisal(domain)

        # Get WHOIS info if not available (or generally)
        registrant = None
        if not availability.available:
            registrant = self._whois_provider.get_registrant(domain)

        # Arthur's rule engine
        is_buy = (
            availability.available is True
            and appraisal.go_value >= 500
            and appraisal.sale_probability >= 0.2
        )

        return DomainEvaluation(
            domain=domain,
            is_available=availability.available,
            go_value=appraisal.go_value,
            sale_probability=appraisal.sale_probability,
            recommendation=Recommendation.BUY if is_buy else Recommendation.SKIP,
            price=availability.price,
            registrant=registrant,
        )


class BatchEvaluateUseCase:
    def __init__(self, evaluate_use_case: EvaluateDomainUseCase):
        self._evaluate_use_case = evaluate_use_case

    def execute(self, domains: List[str]) -> List[DomainEvaluation]:
        return [self._evaluate_use_case.execute(domain) for domain in domains]
