import os
import sys
from dotenv import load_dotenv

from app.infrastructure.config import Settings
from app.infrastructure.godaddy import (
    GoDaddyAvailabilityService,
    GoDaddyAppraisalService,
)
from app.application.use_cases import EvaluateDomainUseCase, BatchEvaluateUseCase
from app.presentation.cli import CLIHandler


def main():
    # 0. Load env vars
    load_dotenv()

    # 1. Infrastructure Setup - Arthur
    settings = Settings.from_env()

    # Check for basic config presence
    if not settings.GODADDY_API_KEY:
        print("Warning: GODADDY_API_KEY not set. API calls will fail.")

    availability_service = GoDaddyAvailabilityService(settings)
    appraisal_service = GoDaddyAppraisalService(settings)

    # 2. Application Setup
    evaluate_use_case = EvaluateDomainUseCase(
        availability_provider=availability_service, appraisal_provider=appraisal_service
    )
    batch_use_case = BatchEvaluateUseCase(evaluate_use_case)

    # 3. Presentation Setup
    # Check if TUI is requested
    if len(sys.argv) > 1 and sys.argv[1] == "tui":
        from app.presentation.tui import DomainIntelApp

        app = DomainIntelApp(batch_use_case)
        app.run()
        return

    cli = CLIHandler(batch_use_case)

    # 4. Input Handling
    # Arthur: In a real app, use argparse. Here we take args or default list.
    domains = sys.argv[1:]
    if not domains:
        print("Usage: python main.py <domain1> ... OR python main.py tui")
        domains = ["example.com", "myawesomestartup123.com", "google.com"]

    cli.run(domains)


if __name__ == "__main__":
    main()
