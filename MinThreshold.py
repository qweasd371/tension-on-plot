import tkinter as tk
from tkinter import ttk
import re
import platform
if platform.platform().startswith("Windows"):
    from unishell import regedit

class MinThreshold:
    """Класс для окна минимального порога"""

    def __init__(self, root: tk.Tk, geometry: str):
        self.root = root
        if platform.platform().startswith("Windows"):
            self.registry = regedit.Registry(regedit.CurUser) / "SOFTWARE" / "T2plot"
        else:
            self.registry = {"min_threshold_value": 0}
        self.geometry = geometry
        self.min_threshold_value = self.registry["min_threshold_value"]
        self.window = None

    def init_window(self):
        if self.window:
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Минимальный порог")
        self.window.geometry(self.geometry)
        self.window.resizable(False, False)
        self.window.transient(self.root)
        self.window.grab_set()

        main = ttk.Frame(self.window, padding=12)
        main.grid(row=0, column=0)

        ttk.Label(main,
                text="Введите минимальный порог:").grid(row=0, column=0, sticky="w", pady=(0, 4))

        vcmd = (self.window.register(self.valid_input), "%P")

        self.entry = ttk.Entry(
            main,
            validate="key",
            validatecommand=vcmd,
            width=24
        )
        self.entry.grid(row=1, column=0, sticky="ew")
        self.entry.insert(0, str(self.min_threshold_value))
        self.entry.focus()

        buttons = ttk.Frame(main)
        buttons.grid(row=2, column=0, sticky="e", pady=(12, 0))

        ttk.Button(buttons,
            text="OK",
            command=self.update_min_threshold).grid(row=0, column=0, padx=(0, 6))

        ttk.Button(buttons,
            text="Отмена",
            command=self.close_window).grid(row=0, column=1)

        self.window.bind("<Return>", self.update_min_threshold)
        self.window.bind("<Escape>", self.close_window)

    def close_window(self, *_):
        if self.window:
            self.window.destroy()
            self.window = None

    def update_min_threshold(self, *_):
        value = self.entry.get().strip()
        if value:
            self.min_threshold_value = float(value)
        self.registry["min_threshold_value"] = self.min_threshold_value
        self.close_window()

    @staticmethod
    def valid_input(text: str, pattern: str = r"\d*(\.?\d{0,2})?") -> bool:
        return re.fullmatch(pattern, text) is not None

    def get_min_threshold(self) -> float:
        return float(self.min_threshold_value)