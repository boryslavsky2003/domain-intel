import tkinter as tk
from tkinter import ttk
import threading
from app.application.use_cases import BatchEvaluateUseCase
from app.domain.models import Recommendation


def rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [
        x1 + radius,
        y1,
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


class RoundedFrame(tk.Canvas):
    def __init__(self, parent, radius=20, bg_color="#303030", **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.radius = radius
        self.bg_color = bg_color

        # Detect parent background for transparency illusion
        try:
            self.parent_bg = parent.cget("background")
        except tk.TclError:
            try:
                self.parent_bg = parent.cget("bg")
            except (tk.TclError, AttributeError):
                self.parent_bg = "#2d2d2d"

        self.configure(bg=self.parent_bg)

        self.inner = tk.Frame(self, bg=bg_color)
        self.win_id = self.create_window(0, 0, window=self.inner, anchor="nw")

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        w, h = event.width, event.height
        self.delete("bg_rect")
        rounded_rect(self, 0, 0, w, h, self.radius, fill=self.bg_color, tags="bg_rect")
        self.tag_lower("bg_rect")

        # Center the inner frame with some padding
        pad_x = self.radius
        pad_y = self.radius // 2
        self.coords(self.win_id, pad_x, pad_y)
        self.itemconfig(self.win_id, width=w - 2 * pad_x, height=h - 2 * pad_y)


class RoundedEntry(tk.Canvas):
    def __init__(
        self,
        parent,
        width,
        height,
        radius=15,
        bg_color="#404040",
        fg_color="white",
        font=("Helvetica", 12),
    ):
        # Match parent bg
        try:
            parent_bg = parent.cget("background")
        except (tk.TclError, AttributeError):
            try:
                parent_bg = parent.cget("bg")
            except (tk.TclError, AttributeError):
                parent_bg = "#2d2d2d"

        super().__init__(
            parent, width=width, height=height, bg=parent_bg, highlightthickness=0
        )

        rounded_rect(self, 0, 0, width, height, radius, fill=bg_color)

        self.entry = tk.Entry(
            self,
            bg=bg_color,
            fg=fg_color,
            font=font,
            borderwidth=0,
            highlightthickness=0,
            insertbackground=fg_color,
        )
        self.create_window(
            width / 2,
            height / 2,
            window=self.entry,
            width=width - 2 * radius,
            height=height - 10,
        )

    def get(self):
        return self.entry.get()


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent,
        text,
        command,
        width=120,
        height=35,
        radius=15,
        bg_color="#404040",
        hover_color="#505050",
        fg_color="white",
    ):
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color

        # Robust parent background detection
        try:
            parent_bg = parent.cget("background")
        except (tk.TclError, AttributeError):
            try:
                parent_bg = parent.cget("bg")
            except (tk.TclError, AttributeError):
                # If all else fails, try style lookup or default
                style = ttk.Style()
                parent_bg = style.lookup("TFrame", "background")
                if not parent_bg:
                    parent_bg = "#2d2d2d"

        super().__init__(
            parent, width=width, height=height, bg=parent_bg, highlightthickness=0
        )

        self.rect = rounded_rect(self, 0, 0, width, height, radius, fill=bg_color)
        self.text = self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=fg_color,
            font=("Helvetica", 10, "bold"),
        )

        self.enable()

    def config(self, **kwargs):
        if "state" in kwargs:
            if kwargs["state"] == "disabled":
                self.disable()
            else:
                self.enable()

    def disable(self):
        self.unbind("<Button-1>")
        self.unbind("<Enter>")
        self.unbind("<Leave>")
        self.itemconfig(self.rect, fill="#555555")

    def enable(self):
        self.bind("<Button-1>", lambda e: self.command())
        self.bind(
            "<Enter>", lambda e: self.itemconfig(self.rect, fill=self.hover_color)
        )
        self.bind("<Leave>", lambda e: self.itemconfig(self.rect, fill=self.bg_color))
        self.itemconfig(self.rect, fill=self.bg_color)


class DomainIntelGUI:
    def __init__(self, batch_use_case: BatchEvaluateUseCase):
        self._batch_use_case = batch_use_case
        self.root = tk.Tk()
        self.root.title("Domain Intel GUI")
        self.root.geometry("1000x700")

        # Glassy effect setup
        self.is_dark = True

        # High transparency for glass feel
        try:
            self.root.wait_visibility(self.root)
            self.root.attributes("-alpha", 0.90)  # Slightly customizable
        except tk.TclError:
            pass

        self.apply_theme()
        self.create_widgets()
        self.animate_window_open()

    def animate_window_open(self):
        try:
            self.fade_in(0)
        except Exception:
            self.root.attributes("-alpha", 0.90)

    def fade_in(self, alpha):
        if alpha < 0.90:
            alpha += 0.05
            self.root.attributes("-alpha", alpha)
            self.root.after(20, lambda: self.fade_in(alpha))
        else:
            self.root.attributes("-alpha", 0.90)

    def apply_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        if self.is_dark:
            # Dark Theme Colors
            self.colors = {
                "bg": "#1e1e2e",
                "fg": "#cdd6f4",
                "card_bg": "#313244",
                "entry_bg": "#45475a",
                "btn_bg": "#313244",
                "success": "#a6e3a1",
                "error": "#f38ba8",
                "header_bg": "#181825",
                "accent": "#89b4fa",
            }
        else:
            # Light Theme Colors
            self.colors = {
                "bg": "#eff1f5",
                "fg": "#4c4f69",
                "card_bg": "#ffffff",
                "entry_bg": "#e6e9ef",
                "btn_bg": "#dce0e8",
                "success": "#40a02b",
                "error": "#d20f39",
                "header_bg": "#dce0e8",
                "accent": "#1e66f5",
            }

        self.root.configure(bg=self.colors["bg"])

        style.configure(
            ".",
            background=self.colors["bg"],
            foreground=self.colors["fg"],
            fieldbackground=self.colors["entry_bg"],
            troughcolor=self.colors["bg"],
            font=("Helvetica", 11),
        )

        style.configure(
            "Treeview",
            background=self.colors["card_bg"],
            foreground=self.colors["fg"],
            fieldbackground=self.colors["card_bg"],
            rowheight=30,
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", self.colors["entry_bg"])])

        style.configure(
            "Treeview.Heading",
            background=self.colors["header_bg"],
            foreground=self.colors["fg"],
            relief="flat",
            font=("Helvetica", 11, "bold"),
        )
        style.map("Treeview.Heading", background=[("active", self.colors["entry_bg"])])

        # Update tag colors if tree exists
        if hasattr(self, "tree"):
            self.update_tags()

    def update_tags(self):
        # Using translucent-like colors
        self.tree.tag_configure(
            "buy",
            background=self.colors["success"] if not self.is_dark else "#0f3d2e",
            foreground=self.colors["fg"],
        )
        self.tree.tag_configure(
            "skip",
            background=self.colors["error"] if not self.is_dark else "#3d1a1f",
            foreground=self.colors["fg"],
        )

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()
        # Recreate widgets to update rounded elements colors is hard,
        # simpler to just update main colors and ask restart for full effect,
        # or implement dynamic update. For now, we update tree and main bg.
        pass  # Full dynamic update for custom drawn widgets requires more code (redraw)

    def create_widgets(self):
        # Main Container
        main_container = tk.Frame(self.root, bg=self.colors["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header Section
        header_frame = tk.Frame(main_container, bg=self.colors["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_lbl = tk.Label(
            header_frame,
            text="Domain Intel AI",
            font=("Helvetica", 20, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
        )
        title_lbl.pack(side=tk.LEFT)

        # Theme toggle (simplified to standard button for now or round)
        # self.theme_btn = RoundedButton(...) # Theme toggle requires redraws, keep it simple?

        # Input Card (Rounded Frame)
        input_card = RoundedFrame(
            main_container, radius=25, bg_color=self.colors["card_bg"], height=160
        )
        input_card.pack(fill=tk.X, pady=(0, 20))

        # Inner content of input card
        inner_input = input_card.inner

        lbl = tk.Label(
            inner_input,
            text="Enter domains to analyze:",
            font=("Helvetica", 11),
            bg=self.colors["card_bg"],
            fg=self.colors["fg"],
        )
        lbl.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))

        self.domain_input = RoundedEntry(
            inner_input,
            width=800,
            height=45,
            radius=10,
            bg_color=self.colors["entry_bg"],
            fg_color=self.colors["fg"],
        )
        self.domain_input.pack(side=tk.TOP, fill=tk.X, pady=(0, 15))
        self.domain_input.entry.bind("<Return>", self.on_submit)

        btn_frame = tk.Frame(inner_input, bg=self.colors["card_bg"])
        btn_frame.pack(fill=tk.X)

        self.submit_btn = RoundedButton(
            btn_frame,
            text="🚀 Evaluate",
            command=self.on_submit,
            width=140,
            height=40,
            radius=20,
            bg_color="#4CAF50",
            hover_color="#45a049",
        )
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.clear_btn = RoundedButton(
            btn_frame,
            text="🧹 Clear",
            command=self.clear_data,
            width=120,
            height=40,
            radius=20,
            bg_color="#f44336",
            hover_color="#d32f2f",
        )
        self.clear_btn.pack(side=tk.LEFT)

        # Progress Bar
        self.progress = ttk.Progressbar(
            main_container, orient=tk.HORIZONTAL, mode="determinate"
        )
        self.progress.pack(fill=tk.X, pady=(0, 15))

        # Results Table
        table_frame = tk.Frame(
            main_container, bg=self.colors["bg"]
        )  # Container for scrollbar + tree
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("DOMAIN", "AVAIL", "PRICE_GOVALUE", "PROB", "OWNER", "DECISION")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", style="Treeview"
        )

        self.tree.heading("DOMAIN", text="DOMAIN")
        self.tree.heading("AVAIL", text="AVAIL")
        self.tree.heading("PRICE_GOVALUE", text="$ PRICE")
        self.tree.heading("PROB", text="% PROB")
        self.tree.heading("OWNER", text="OWNER")
        self.tree.heading("DECISION", text="DECISION")

        # Column configuration
        self.tree.column("DOMAIN", width=220)
        self.tree.column("AVAIL", width=80, anchor="center")
        self.tree.column("PRICE_GOVALUE", width=120)
        self.tree.column("PROB", width=80, anchor="center")
        self.tree.column("OWNER", width=150)
        self.tree.column("DECISION", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
        self.domain_input.entry.focus()

    def clear_data(self):
        self.tree.delete(*self.tree.get_children())
        self.domain_input.entry.delete(0, tk.END)
        self.progress["value"] = 0

    def run(self):
        self.root.mainloop()
