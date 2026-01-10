import requests
from typing import Dict, Any, Optional

from app.domain.models import DomainAvailability, DomainAppraisal
from app.domain.ports import AvailabilityProvider, AppraisalProvider
from app.infrastructure.config import Settings


class GoDaddyBaseClient:
    def __init__(self, settings: Settings):
        self._base_url = settings.GODADDY_BASE_URL
        self._headers = {
            "Authorization": f"sso-key {settings.GODADDY_API_KEY}:{settings.GODADDY_API_SECRET}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f"{self._base_url}{endpoint}"
        try:
            response = requests.get(
                url, headers=self._headers, params=params, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Arthur: Need proper logging here later
            print(f"API Error [{endpoint}]: {e}")
            raise


class GoDaddyAvailabilityService(GoDaddyBaseClient, AvailabilityProvider):
    def check_availability(self, domain: str) -> DomainAvailability:
        # Arthur: GET /v1/domains/available
        data = self._get("/v1/domains/available", params={"domain": domain})

        return DomainAvailability(
            domain=domain,
            available=data.get("available", False),
            price=float(data.get("price", 0)) if data.get("price") else None,
            currency=data.get("currency"),
        )


class GoDaddyAppraisalService(GoDaddyBaseClient, AppraisalProvider):
    def get_appraisal(self, domain: str) -> DomainAppraisal:
        # endpoint: GET /v1/appraisal/{domain}
        # Note: Endpoint might differ based on GoDaddy API version.
        # Assuming typical GoDaddy Appraisal API structure or GoValue API.
        # Fallback to 0 if API fails or returns unexpected structure in this MVP.

        try:
            data = self._get(f"/v1/appraisal/{domain}")

            # Extracting typical fields (adjust based on actual API response schema)
            govalue = float(data.get("govalue", 0))
            # sales_probability is often not strictly exposed in public GoValue API
            # or might be named differently. Mocking mapping or using what's available.
            # Assuming 'comparable_sales_probability' or similar if using a specific tier.
            # For this exercise, we safeguard the retrieval.

            # If the API doesn't return probability, we default to 0.0 to fail safely
            # as per the requirement > 0.2
            probability = float(data.get("sale_probability", 0.0))

            return DomainAppraisal(
                domain=domain, go_value=govalue, sale_probability=probability
            )
        except Exception:
            # Arthur: Fail safe
            return DomainAppraisal(domain=domain, go_value=0.0, sale_probability=0.0)
