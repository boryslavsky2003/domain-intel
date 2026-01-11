import tkinter as tk
from tkinter import ttk
import threading
from app.application.use_cases import BatchEvaluateUseCase
from app.domain.models import Recommendation


class DomainIntelGUI:
    def __init__(self, batch_use_case: BatchEvaluateUseCase):
        self._batch_use_case = batch_use_case
        self.root = tk.Tk()
        self.root.title("Domain Intel GUI")
        self.root.geometry("900x600")

        self.is_dark = True
        self.apply_theme()
        self.create_widgets()

    def apply_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")  # 'clam' works well for custom styling

        if self.is_dark:
            bg_color = "#2d2d2d"
            fg_color = "#ffffff"
            entry_bg = "#3d3d3d"
            select_bg = "#4a4a4a"
            heading_bg = "#404040"
            heading_active = "#505050"
            btn_bg = "#404040"
            btn_active = "#505050"
            btn_disabled = "#2d2d2d"
            btn_fg_disabled = "#808080"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            entry_bg = "#ffffff"
            select_bg = "#d9d9d9"
            heading_bg = "#e0e0e0"
            heading_active = "#d0d0d0"
            btn_bg = "#e0e0e0"
            btn_active = "#d0d0d0"
            btn_disabled = "#f0f0f0"
            btn_fg_disabled = "#a0a0a0"

        self.root.configure(bg=bg_color)

        style.configure(
            ".",
            background=bg_color,
            foreground=fg_color,
            fieldbackground=entry_bg,
            troughcolor=bg_color,
        )

        style.configure(
            "Treeview",
            background=entry_bg,
            foreground=fg_color,
            fieldbackground=entry_bg,
            rowheight=25,
        )
        style.map("Treeview", background=[("selected", select_bg)])

        style.configure(
            "Treeview.Heading",
            background=heading_bg,
            foreground=fg_color,
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", heading_active)])

        style.configure("TEntry", fieldbackground=entry_bg, foreground=fg_color)
        style.configure(
            "TButton", background=btn_bg, foreground=fg_color, borderwidth=1
        )
        style.map(
            "TButton",
            background=[("active", btn_active), ("disabled", btn_disabled)],
            foreground=[("disabled", btn_fg_disabled)],
        )

        # Update tag colors if tree exists
        if hasattr(self, "tree"):
            self.update_tags()

    def update_tags(self):
        if self.is_dark:
            self.tree.tag_configure("buy", background="#155724", foreground="#d4edda")
            self.tree.tag_configure("skip", background="#721c24", foreground="#f8d7da")
        else:
            self.tree.tag_configure("buy", background="#d1e7dd", foreground="black")
            self.tree.tag_configure("skip", background="#f8d7da", foreground="black")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    def create_widgets(self):
        # Frame for Input
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        lbl = ttk.Label(input_frame, text="Введіть домени (через пробіл або кому):")
        # Arthur: Using pack like in a layout manager
        lbl.pack(side=tk.TOP, anchor=tk.W)

        self.domain_input = ttk.Entry(input_frame)
        self.domain_input.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.domain_input.bind("<Return>", self.on_submit)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.submit_btn = ttk.Button(btn_frame, text="Evaluate", command=self.on_submit)
        self.submit_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_data)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.theme_btn = ttk.Button(
            btn_frame, text="Toggle Theme", command=self.toggle_theme
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(
            self.root, orient=tk.HORIZONTAL, mode="determinate"
        )
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Table
        columns = ("DOMAIN", "AVAIL", "PRICE_GOVALUE", "PROB", "OWNER", "DECISION")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        self.tree.heading("DOMAIN", text="DOMAIN")
        self.tree.heading("AVAIL", text="AVAIL")
        self.tree.heading("PRICE_GOVALUE", text="PRICE / GOVALUE")
        self.tree.heading("PROB", text="PROB")
        self.tree.heading("OWNER", text="OWNER")
        self.tree.heading("DECISION", text="DECISION")

        # Column configuration
        self.tree.column("DOMAIN", width=150)
        self.tree.column("AVAIL", width=80)
        self.tree.column("PRICE_GOVALUE", width=150)
        self.tree.column("PROB", width=80)
        self.tree.column("OWNER", width=150)
        self.tree.column("DECISION", width=100)

        scrollbar = ttk.Scrollbar(
            self.root, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Style tags
        self.update_tags()

    def on_submit(self, event=None):
        text = self.domain_input.get()
        if not text:
            return

        domains = [d.strip() for d in text.replace(",", " ").split() if d.strip()]
        if not domains:
            return

        self.submit_btn.config(state=tk.DISABLED)
        # self.domain_input.config(state=tk.DISABLED) # Optional: disable input
        self.tree.delete(*self.tree.get_children())
        self.progress["maximum"] = len(domains)
        self.progress["value"] = 0

        # Start processing in a thread
        threading.Thread(
            target=self.process_domains, args=(domains,), daemon=True
        ).start()

    def process_domains(self, domains):
        for domain in domains:
            try:
                # We process one by one to update UI
                results = self._batch_use_case.execute([domain])

                if results:
                    res = results[0]
                    self.root.after(0, self.add_result, res)
            except Exception as e:
                print(f"Error processing {domain}: {e}")

            self.root.after(0, self.step_progress)

        self.root.after(0, self.finish_processing)

    def step_progress(self):
        self.progress["value"] += 1

    def add_result(self, res):
        # Format similar to TUI
        price_val = f"${res.price}" if res.price else f"${res.go_value or 0}"
        prob = f"{int((res.sale_probability or 0) * 100)}%"
        registrant = res.registrant or "N/A"
        decision = "BUY" if res.recommendation == Recommendation.BUY else "SKIP"

        # Color coding (Treeview tags)
        tag = "buy" if res.recommendation == Recommendation.BUY else "skip"

        self.tree.insert(
            "",
            tk.END,
            values=(
                res.domain,
                "YES" if res.is_available else "NO",
                price_val,
                prob,
                registrant,
                decision,
            ),
            tags=(tag,),
        )

    def finish_processing(self):
        self.submit_btn.config(state=tk.NORMAL)
        self.domain_input.config(state=tk.NORMAL)
        self.domain_input.focus()

    def clear_data(self):
        self.tree.delete(*self.tree.get_children())
        self.domain_input.delete(0, tk.END)
        self.progress["value"] = 0

    def run(self):
        self.root.mainloop()
