import sys
import tkinter as tk
from tkinter import filedialog 
from pathlib import Path
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
except ModuleNotFoundError:
    print("Библиотека matplotlib не установлена.")
    sys.exit(1)

class Main():
    def __init__(self, list_data: list = [], 
                 file_name: str = "",
                 width: int = 600, height: int = 800,
                 dpi: int = 100,
                 time: int | float = 0.001):
        
        self.list_data = list_data
        self.file_name = file_name
        self.width = width
        self.height = height
        self.dpi = dpi
        self.time = int(time * 1000)
        self.line_values = []
    
        # Создание окна
        self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")

        # Создаём иформационные надписи
        self.info_lable1 = tk.Label(self.root, text="Средне статистическое: 0.0000")
        self.info_lable2 = tk.Label(self.root, text="Средне статистическое (без учёта нулей): 0.0000")
        self.info_lable3 = tk.Label(self.root, text="Максимальное значение: 0.0000")
        self.info_lable1.place(y=0, x=0)
        self.info_lable2.place(y=18, x=0)
        self.info_lable3.place(y=36, x=0)

        # Создаём поле ввода названия файла или путя
        self.file_name_entry = tk.Entry(self.root, width=50)
        self.file_name_entry.place(y=55, x=0)

        # Создаём кнопку обновления названия файла или пути 
        self.file_name_update_button = tk.Button(self.root, text="Обновить название фаила.", command=self.update_file_name)
        self.file_name_update_button.place(y=55, x=360)

        # Создаём кнопку для запроса файла
        self.file_name_ask_path = tk.Button(self.root, text="Обзор", command=self.ask_path)
        self.file_name_ask_path.place(y=85, x=360)

        # "Биндим" функции на различные действия
        self._focus_out_file_name_entry()
        self.file_name_entry.bind("<Return>", self.update_file_name)
        self.file_name_entry.bind("<FocusIn>", self._focus_in_file_name_entry)
        self.file_name_entry.bind("<FocusOut>", self._focus_out_file_name_entry)

        # Создаём кнопку загрузки и начала отрисовки 
        self.load_file_button = tk.Button(self.root, text="Загрузить файл", command=self.load_file)
        self.load_file_button.place(y=75, x=0)

        # Создаём кнопку остановки
        self.stop_button = tk.Button(self.root, text="Завершить отрисовку", command=self.stop)
        self.stop_button.place(y=105, x=0)
        
        # Инициализируем график
        self.fig = Figure((self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("F, Н")
        self.ax.set_xlabel("t, мс")
        self.line, = self.ax.plot(range(len(self.list_data)), self.list_data, "o-")

        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas.get_tk_widget().pack(pady=135)
        
        # Зацикливаем
        self.root.mainloop()

    def load_file(self):
        "Загрузка фаила."
        with open(self.file_name, "r", encoding="utf-8") as file:
            self.line_values = [float(i) for i in file.read().splitlines() if i.strip()]

            # Очиняем и обновляем график
            self.ax.clear()
            self.line, = self.ax.plot([], [], "o-")

            # Ставим названия сторон
            self.ax.set_ylabel("F, Н")
            self.ax.set_xlabel("t, мс")
            self.list_data = []

            # Начинаем отрисовку
            self._add_step_for_line()

            # Закрываем файл
            file.close()
        
    def ask_path(self):
        "Обзор фаилов."
        self.file_name = filedialog.askopenfilename(title="Выберете файл.", filetypes=[("Текстовые файлы.", "*.txt"),
                                                                                        ("Все файлы.", "*.*")])
        self.file_name_entry.delete(0, tk.END)
        self.file_name_entry.insert(tk.END, self.file_name)

    def _add_step_for_line(self):
        "Шаг отрисовки."
        if self.line_values:
            # Обновление информациональных надписей
            self.update_info_label()

            self.list_data.append(self.line_values.pop(0))

            # Обновляет данные
            self.line.set_data([i * self.time for i in range(len(self.list_data))], self.list_data)
            self.ax.relim()
            self.ax.autoscale_view()

            # Отрисовка графика
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.root.after(self.time, self._add_step_for_line)
    
    def stop(self):
        "Остановка отрисовки."
        self.line_values = []
    
    def update_info_label(self, *argv):
        "Обновление информациональных надписей."
        self.info_lable1.config(text=f"Средне статистическое: {self.mean(self.list_data):.4f}")
        self.info_lable2.config(text=f"Средне статистическое (без учёта нулей): {self.mean(self.list_data, True):.4f}")
        self.info_lable3.config(text=f"Максимальное значение: {max(self.list_data) if self.list_data else 0:.4f}")
    
    def update_file_name(self, *argv):
        "Обновление названия файла или путь."
        # Если это файл
        if Path(self.file_name).is_file():
            self.file_name = self.file_name_entry.get()
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.insert(tk.END, "Сохранено!")
        # Если это не файл
        else:
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.insert(tk.END, "Таково файла не существует.")

    def _focus_in_file_name_entry(self, *argv):
        "Фокус на виджет."
        if self.file_name_entry.get().strip() in ["Введите название фаила.", "Сохранено!", "Таково файла не существует."] :
            self.file_name_entry.delete(0, tk.END)
    
    def _focus_out_file_name_entry(self, *argv):
        "Фокус с виджета."
        if not self.file_name_entry.get().split():
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.insert(tk.END, "Введите название фаила.")

    @staticmethod
    def mean(list_data, without_zero: bool = False):
        "Средне арифметическое."
        x = []
        if without_zero:
            x = [i for i in list_data if i]
        else:
            x = [i for i in list_data]
        if x:
            return sum(x) / len(x)
        else:
            return 0
        
if __name__ == "__main__":
    Main()