from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, DataTable, Static, ProgressBar
from textual import work
from app.application.use_cases import BatchEvaluateUseCase
from app.domain.models import Recommendation


class DomainIntelApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    Input {
        dock: top;
        margin: 1 0;
    }
    DataTable {
        height: 1fr;
        border: solid green;
    }
    .intro {
        padding: 1;
        text-align: center;
        background: $primary;
        color: auto;
    }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("c", "clear_data", "Clear results"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, batch_use_case: BatchEvaluateUseCase):
        super().__init__()
        self._batch_use_case = batch_use_case

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Введіть домени (через пробіл або кому) та натисніть Enter:",
            classes="intro",
        )
        yield Input(placeholder="google.com example.com...")
        yield ProgressBar(show_eta=False)
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(
            "DOMAIN", "AVAIL", "PRICE/GOVALUE", "PROB", "OWNER", "DECISION"
        )

    def action_clear_data(self) -> None:
        """Clear the table and reset input."""
        self.query_one(DataTable).clear()
        self.query_one(ProgressBar).update(total=100, progress=0)
        inp = self.query_one(Input)
        inp.disabled = False
        inp.value = ""
        inp.focus()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        if not message.value:
            return

        domains = [
            d.strip() for d in message.value.replace(",", " ").split() if d.strip()
        ]
        if domains:
            self.query_one(Input).disabled = True
            self.process_domains(domains)

    @work(exclusive=True)
    async def process_domains(self, domains: list[str]) -> None:
        table = self.query_one(DataTable)
        table.clear()

        progress = self.query_one(ProgressBar)
        progress.update(total=len(domains), progress=0)

        # Arthur: Using loop executor to avoid blocking UI with sync calls
        import asyncio

        loop = asyncio.get_running_loop()

        for i, domain in enumerate(domains):
            # Process one at a time to update progress
            results = await loop.run_in_executor(
                None, self._batch_use_case.execute, [domain]
            )

            # Since we process one by one, results header is 1 element
            if not results:
                continue

            res = results[0]
            decision = "BUY" if res.recommendation == Recommendation.BUY else "SKIP"

            # Arthur: Formatting strings for TUI
            avail_str = "YES" if res.is_available else "NO"

            if res.is_available and res.price is not None:
                price_str = f"${res.price:,.2f}"
            else:
                price_str = f"${res.go_value:,.2f}"

            prob_str = f"{res.sale_probability:.0%}"

            # Format registrant info
            owner_str = res.registrant if res.registrant else "-"

            table.add_row(
                res.domain, avail_str, price_str, prob_str, owner_str, decision
            )

            # Update progress
            progress.advance(1)
