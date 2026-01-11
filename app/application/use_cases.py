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

        # Advanced Analysis
        is_buy = self._analyze_potential(domain, availability, appraisal)

        return DomainEvaluation(
            domain=domain,
            is_available=availability.available,
            go_value=appraisal.go_value,
            sale_probability=appraisal.sale_probability,
            recommendation=Recommendation.BUY if is_buy else Recommendation.SKIP,
            price=availability.price,
            registrant=registrant,
        )

    def _analyze_potential(
        self,
        domain: str,
        availability: DomainAvailability,
        appraisal: DomainAppraisal,
    ) -> bool:
        """
        Comprehensive domain evaluation logic.
        Analyzes TLD tier, structure, length, availability, and financial metrics.
        """
        # 0. Basic Availability Check
        if not availability.available:
            return False

        # 1. TLD Analysis
        tld = domain.split(".")[-1].lower()
        premium_tlds = {"com", "ai", "io"}
        standard_tlds = {"net", "org", "co", "app", "dev"}

        # Base thresholds
        min_value = 500.0
        min_prob = 0.2

        if tld in premium_tlds:
            min_value = 500  # Keep standard for premium
        elif tld in standard_tlds:
            min_value = 1000  # Higher bar for standard
            min_prob = 0.3
        else:
            # Obscure TLDs need very high stats to be worth flipping
            min_value = 2500
            min_prob = 0.4

        # 2. Structure Check (Hyphens and Numbers)
        domain_name = domain.split(".")[0]

        # Hyphens: Generally reduce resale liquidity
        if "-" in domain_name:
            if domain_name.count("-") > 1:
                return False  # More than 1 hyphen is usually junk
            min_value += 500  # Raise bar for hyphenated domains

        # Numbers: Digits mixed with letters usually bad
        if any(char.isdigit() for char in domain_name):
            # Pure numeric (e.g. 888.com) is good, but mixed (buy4you) is bad
            if not domain_name.isdigit():
                # Unless very short, mixed alphanumeric is hard to sell
                if len(domain_name) > 6:
                    return False
                min_value += 500

        # 3. Length Check
        # Shorter is better.
        if len(domain_name) > 20:
            return False

        # 4. Financial Viability (ROI Check)
        # If we have a buy price, ensure potential profit margin
        if availability.price and availability.price > 0:
            # We want at least 3x potential return based on GoValue
            # e.g. Buy for $1000, GoValue should be $3000+
            if appraisal.go_value < (availability.price * 3):
                return False

            # Hard cap on investment risk (e.g. don't suggest buying $5000 domains automatically)
            if availability.price > 2000:
                # Unless it's an amazing deal (10x)
                if appraisal.go_value < (availability.price * 10):
                    return False

        # Final Decision
        return (
            appraisal.go_value >= min_value and appraisal.sale_probability >= min_prob
        )


class BatchEvaluateUseCase:
    def __init__(self, evaluate_use_case: EvaluateDomainUseCase):
        self._evaluate_use_case = evaluate_use_case

    def execute(self, domains: List[str]) -> List[DomainEvaluation]:
        return [self._evaluate_use_case.execute(domain) for domain in domains]
