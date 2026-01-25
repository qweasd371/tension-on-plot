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

        self.entry = tk.Entry(self.min_threshold_window, validate="key", validatecommand=vcmd, width=20)
        self._out_focus()
        self.entry.bind("<FocusIn>", self._in_focus)
        self.entry.bind("<FocusOut>", self._out_focus)
        self.entry.pack(anchor="w")

        self.update_button = tk.Button(self.min_threshold_window, text="Сохранить", command=self.update_min_threshold, width=13)
        self.update_button.place(x=0, y=30)
        self.close_button = tk.Button(self.min_threshold_window, text="Отмена", command=self.close_window, width=13)
        self.close_button.place(x=100, y=30)

        self.is_window_init = True
    
    def close_window(self):
        if self.is_window_init:
            self.min_threshold_window.destroy()
            self.is_window_init = False

    def update_min_threshold(self):
        """Обновить значение минимального порога"""
        if self.entry.get() and self.entry.get().split() not in ("Введите число", "Сохранено!"):
            try:
                self.min_threshold_value = float(self.entry.get())
            except ValueError:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Ошибка конвертации в число")
                self.min_threshold_window.after(3000, self._insert_save_min_threshold)
            else:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, "Сохранено!")
                self.min_threshold_window.after(3000, self._insert_save_min_threshold)

    @staticmethod
    def valid_input(text:str, pattern:str = r"\d*(\.?\d{0,2})?", excepts:tuple = ("Введите число", "Сохранено!", "Ошибка конвертации в число")) -> bool:
        """Проверка текста под патерн"""
        if text in excepts:
            return True
        return not(re.fullmatch(pattern, text) is None)

    def get_min_threshold(self) -> float:
        return self.min_threshold_value

    def _in_focus(self, *_):
        if self.entry.get().strip() in ("Введите число", "Сохранено!", "Ошибка конвертации в число"):
            self.entry.delete(0, tk.END)
    
    def _out_focus(self, *_):
        if not self.entry.get().strip():
            self.entry.insert(0, "Введите число")
    
    def _insert_save_min_threshold(self):
        if self.entry.get().strip() in ("Сохранено!", "Ошибка конвертации в число"):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(self.min_threshold_value))