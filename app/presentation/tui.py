from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, DataTable, Static
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
        ("q", "quit", "Quit"),
    ]

    def __init__(self, batch_use_case: BatchEvaluateUseCase):
        super().__init__()
        self._batch_use_case = batch_use_case

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Введіть домени (через кому) та натисніть Enter:", classes="intro")
        yield Input(placeholder="google.com, example.com...")
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("DOMAIN", "AVAIL", "PRICE/GOVALUE", "PROB", "DECISION")

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        if not message.value:
            return

        domains = [d.strip() for d in message.value.split(",") if d.strip()]
        if domains:
            self.query_one(Input).disabled = True
            self.process_domains(domains)

    @work(exclusive=True)
    async def process_domains(self, domains: list[str]) -> None:
        table = self.query_one(DataTable)
        table.clear()

        # Arthur: Using loop executor to avoid blocking UI with sync calls
        import asyncio

        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None, self._batch_use_case.execute, domains
        )

        for res in results:
            decision = "BUY" if res.recommendation == Recommendation.BUY else "SKIP"

            # Arthur: Formatting strings for TUI
            avail_str = "YES" if res.is_available else "NO"
            price_str = f"${res.go_value:,.2f}"
            prob_str = f"{res.sale_probability:.0%}"

            table.add_row(res.domain, avail_str, price_str, prob_str, decision)

        self.query_one(Input).disabled = False
        self.query_one(Input).value = ""
        self.query_one(Input).focus()
