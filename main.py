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
                 file: str = "",
                 width: int = 600, height: int = 800,
                 dpi: int = 100,
                 time: int | float = 0.001):
        
        self.list_data = list_data
        self.file = file
        self.width = width
        self.height = height
        self.dpi = dpi
        self.time = int(time * 1000)
        self.line_values = []
    
        # Создание окна
        self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")

        # Создаём информационную надпись
        self.info_lable = tk.Label(self.root, text="Максимальное значение: 0.0000")
        self.info_lable.place(y=0, x=0)

        # Создаём поле ввода названия файла или путя
        self.file_entry = tk.Entry(self.root, width=50)
        self.file_entry.place(y=30, x=0)

        # Создаём кнопку обновления названия файла или пути 
        self.file_update_button = tk.Button(self.root, text="Загрузить файл", command=self.update_file)
        self.file_update_button.place(y=30, x=360)

        # Создаём кнопку для запроса файла
        self.file_ask_path = tk.Button(self.root, text="Обзор", command=self.ask_path)
        self.file_ask_path.place(y=60, x=360)

        # "Биндим" функции на различные действия
        self._focus_out_file_entry()
        self.file_entry.bind("<Return>", self.update_file)
        self.file_entry.bind("<FocusIn>", self._focus_in_file_entry)
        self.file_entry.bind("<FocusOut>", self._focus_out_file_entry)

        # Создаём кнопку загрузки и начала отрисовки 
        self.load_file_button = tk.Button(self.root, text="Начать отрисовку", command=self.load_file)
        self.load_file_button.place(y=60, x=0)

        # Создаём кнопку остановки
        self.stop_button = tk.Button(self.root, text="Завершить отрисовку", command=self.stop)
        self.stop_button.place(y=90, x=0)
        
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
        self.canvas.get_tk_widget().pack(pady=120)
        
        # Зацикливаем
        self.root.mainloop()

    def load_file(self):
        "Загрузка фаила."
        with open(self.file, "r", encoding="utf-8") as f:
            self.line_values = [float(i) for i in f.read().splitlines() if i.strip()]

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
            f.close()
        
    def ask_path(self):
        "Обзор фаилов."
        self.file = filedialog.askopenfilename(title="Выберете файл.", filetypes=[("Текстовые файлы.", "*.txt"),
                                                                                        ("Все файлы.", "*.*")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(tk.END, self.file)

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
        "Обновление информационной надписи."
        self.info_lable.config(text=f"Максимальное значение: {max(self.list_data) if self.list_data else 0:.4f}")
    
    def update_file(self, *argv):
        "Обновление названия файла или путь."
        # Если это файл
        if Path(self.file).is_file():
            self.file = self.file_entry.get()
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, "Сохранено!")
        # Если это не файл
        else:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, "Таково файла не существует.")

    def _focus_in_file_entry(self, *argv):
        "Фокус на виджет."
        if self.file_entry.get().strip() in ["Введите название файла.", "Сохранено!", "Таково файла не существует."] :
            self.file_entry.delete(0, tk.END)
    
    def _focus_out_file_entry(self, *argv):
        "Фокус с виджета."
        if not self.file_entry.get().split():
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, "Введите название файла.")
        
if __name__ == "__main__":
    Main()