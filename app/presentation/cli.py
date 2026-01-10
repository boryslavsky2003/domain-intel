from typing import List
from app.application.use_cases import BatchEvaluateUseCase
from app.domain.models import Recommendation


class CLIHandler:
    def __init__(self, batch_use_case: BatchEvaluateUseCase):
        self._batch_use_case = batch_use_case

    def run(self, domains: List[str]):
        print(f"Processing {len(domains)} domains...\n")

        try:
            results = self._batch_use_case.execute(domains)

            print(
                f"{'DOMAIN':<25} | {'AVAIL':<8} | {'GOVALUE':<10} | {'PROB':<6} | {'DECISION'}"
            )
            print("-" * 75)

            for res in results:
                decision = "BUY" if res.recommendation == Recommendation.BUY else "SKIP"
                color = "\033[92m" if decision == "BUY" else "\033[91m"
                reset = "\033[0m"

                print(
                    f"{res.domain:<25} | "
                    f"{str(res.is_available):<8} | "
                    f"${int(res.go_value):<9} | "
                    f"{res.sale_probability:<6} | "
                    f"{color}{decision}{reset}"
                )
        except Exception as e:
            print(f"Error executing batch: {e}")
