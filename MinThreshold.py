import tkinter as tk
import re
class MinThreshold:
    """Класс для окна минимального порога"""
    def __init__(self, geometry: str):
        self.geometry = geometry
        self.is_window_init = False
        self.min_threshold_value = 0

    def init_window(self):
        """Инициализировать окно"""
        self.min_threshold_window = tk.Tk()
        self.min_threshold_window.geometry(self.geometry)
        self.min_threshold_window.title("Минимальный порог")
        self.min_threshold_window.resizable(False, False)

        vcmd = (self.min_threshold_window.register(self.valid_input), "%P")

        self.entry = tk.Entry(self.min_threshold_window, validate="key", validatecommand=vcmd, width=10)
        self.entry.pack()

        self.update_button = tk.Button(self.min_threshold_window, text="Обновит минимальный порог\nи закрыть окно", command=lambda: (self.update_min_threshold(), self.close_window()))
        self.update_button.pack()

        self.is_window_init = True
    
    def close_window(self):
        if self.is_window_init:
            self.min_threshold_window.destroy()
            self.is_window_init = False

    def update_min_threshold(self):
        """Обновить значение минимального порога"""
        if self.entry.get():
            self.min_threshold_value = float(self.entry.get())

    @staticmethod
    def valid_input(text:str, pattern:str = r"\d*(\.?\d{0,2})?") -> bool:
        """Проверка текста под патерн"""
        return not(re.fullmatch(pattern, text) is None)

    def get_min_threshold(self) -> float:
        return self.min_threshold_value
