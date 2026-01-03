import sys
import tkinter as tk
from tkinter import filedialog 
try:
    import serial
except ModuleNotFoundError:
    print("Библиотека pyserial не установлена.")
    sys.exit(1)
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
                 time: int | float = 0.001,
                 min_threshold: float = 0.5):
        
        self.list_data = list_data
        self.file = file
        self.width = width
        self.height = height
        self.dpi = dpi
        self.time = int(time * 1000)
        self.line_values = []
        self.min_threshold = min_threshold

        # Создание окна
        self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")
        
        self.plot_group_settings = tk.LabelFrame(self.root,
                                            text="Управление графика",
                                            relief="solid",
                                            padx=5,
                                            pady=5,
                                            height=90,
                                            width=90)
        self.plot_group_settings.pack(anchor="nw", padx=10, pady=10, fill="both", expand=False)
        
        # Создаём кнопку загрузки и начала отрисовки 
        self.load_file_button = tk.Button(self.plot_group_settings, text="Начать отрисовку", command=self.load_file)
        self.load_file_button.pack(anchor="nw")

        # Создаём кнопку остановки
        self.stop_button = tk.Button(self.plot_group_settings, text="Завершить отрисовку", command=self.stop)
        self.stop_button.pack(anchor="nw")

        self.file_group_settings = tk.LabelFrame(self.root,
                                                text="Управление фаила",
                                                relief="solid",
                                                padx=5,
                                                pady=5,
                                                height=90,
                                                width=90)
        self.file_group_settings.pack(anchor="nw", padx=10, pady=10, fill="both", expand=False)

        # Создаём поле ввода названия файла или путя
        self.file_entry = tk.Entry(self.file_group_settings, width=50)
        self.file_entry.pack(anchor="nw")

        # Создаём кнопку обновления названия файла или пути 
        self.file_update_button = tk.Button(self.file_group_settings, text="Загрузить файл", command=self.update_file)
        self.file_update_button.pack(anchor="nw")

        # Создаём кнопку для запроса файла
        self.file_ask_path = tk.Button(self.file_group_settings, text="Обзор", command=self.ask_path)
        self.file_ask_path.pack(anchor="nw")

        # "Биндим" функции на различные действия
        self._focus_out_file_entry()
        self.file_entry.bind("<Return>", self.update_file)
        self.file_entry.bind("<FocusIn>", self._focus_in_file_entry)
        self.file_entry.bind("<FocusOut>", self._focus_out_file_entry)

        
        # Создаём поле ввода ввода минимального порога чисел
        self.min_threshold_entry = tk.Entry(self.plot_group_settings, width=50)
        self.min_threshold_entry.pack(anchor="nw")

        # "Биндим" функции на различные действия
        self._focus_out_min_threshold_entry()
        self.min_threshold_entry.bind("<Return>", self.update_min_threshold)
        self.min_threshold_entry.bind("<FocusIn>", self._focus_in_min_threshold_entry)
        self.min_threshold_entry.bind("<FocusOut>", self._focus_out_min_threshold_entry)

        # Создаём кнопки обновления минимального порога чисел
        self.min_threshold_button = tk.Button(self.plot_group_settings, text="Обновить минимальный порог", command=self.update_min_threshold)
        self.min_threshold_button.pack(anchor="nw")

        # Инициализируем график
        self.fig = Figure((self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("m, т")
        self.ax.set_xlabel("t, мс")
        self.line, = self.ax.plot(range(len(self.list_data)), self.list_data, "o-")

        self.plot_group = tk.LabelFrame(self.root,
                                        text="График",
                                        relief="solid",
                                        padx=5,
                                        pady=5,)
        self.plot_group.pack(anchor="nw", padx=10, pady=10, fill="both")

        # Создаём информационную надпись
        self.info_label = tk.Label(self.plot_group, text="Максимальное значение: 0.0000")
        self.info_label.pack(anchor="nw")

        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_group)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_group)
        toolbar.update()
        self.canvas.get_tk_widget().pack(anchor="nw")
        
        # Зацикливаем
        self.root.mainloop()

    def load_file(self):
        "Загрузка фаила."
        with open(self.file_name, "r", encoding="utf-8") as file:
            self.line_values = []
            for line_value in file.read().splitlines():
                line_value = line_value[:line_value.rfind("]")][:line_value.find("[")]
                if line_value and float(line_value) >= self.min_threshold:
                    self.line_values.append(float(line_value))
            # Закрываем файл
            file.close()
        self.line_values = self.remove_double(self.line_values)
        # Очиняем и обновляем график
        self.list_data = []
        self.ax.clear()
        self.line, = self.ax.plot([], [], "o-")

        # Ставим названия сторон
        self.ax.set_ylabel("m, т")
        self.ax.set_xlabel("t, мс")
            
        # Начинаем отрисовку
        self._add_step_for_line()
        
    def ask_path(self):
        "Обзор фаилов."
        self.file_name = filedialog.askopenfilename(title="Выберете файл.", filetypes=[("Текстовые файлы.", "*.txt"),
                                                                                        ("Все файлы.", "*.*")])
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(tk.END, self.file_name)

    def _add_step_for_line(self):
        "Шаг отрисовки."
        if self.line_values:
            # Обновление информациональных надписей
            self.update_info_label()
            x = self.line_values.pop(0)
            self.list_data.append(x)

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
        self.info_label.config(text=f"Максимальное значение: {max(self.list_data) if self.list_data else 0:.4f}")
    
    def update_file(self, *argv):
        "Обновление названия файла или путь."
        try:
            open(self.file_name)
        except FileNotFoundError:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, "Таково файла не существует.")
        else:
            self.file = self.file_entry.get()
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, "Сохранено!")
            self.root.after(2000, lambda: (self.file_entry.delete(0, tk.END),
                                           self.file_entry.insert(tk.END, self.file)))
            
    def update_min_threshold(self, *argv):
        "Обновление минимального порога"
        try:
            min_threshold_file = self.min_threshold_entry.get()
            self.min_threshold = float(min_threshold_file)
            self.min_threshold_entry.delete(0, tk.END)
            self.min_threshold_entry.insert(tk.END, "Сохранено!")
            self.root.after(2000, lambda: (self.min_threshold_entry.delete(0, tk.END),
                                           self.min_threshold_entry.insert(tk.END, self.min_threshold)))
        except ValueError:
            self.min_threshold_entry.delete(0, tk.END)
            self.min_threshold_entry.insert(tk.END, "Число не возможно перевести в дробь.")

    def _focus_in_min_threshold_entry(self, *argv):
        "Фокус на виджет."
        if self.min_threshold_entry.get().strip() in ["Число не возможно перевести в дробь.", "Сохранено!", "Введите минимальный порог."]:
            self.min_threshold_entry.delete(0, tk.END)
    
    def _focus_out_min_threshold_entry(self, *argv):
        "Фокус с виджета."
        if not self.min_threshold_entry.get().strip():
            self.min_threshold_entry.delete(0, tk.END)
            self.min_threshold_entry.insert(tk.END, "Введите минимальный порог.")

    def _focus_in_file_entry(self, *argv):
        "Фокус на виджет."
        if self.file_entry.get().strip() in ["Введите название файла.", "Сохранено!", "Таково файла не существует."] :
            self.file_entry.delete(0, tk.END)
    
    def _focus_out_file_entry(self, *argv):
        "Фокус с виджета."
        if not self.file_entry.get().split():
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(tk.END, "Введите название файла.")
    
    @staticmethod
    def remove_double(lst: list | tuple):
        "Удаление дубликатов в списке."
        result = []
        last = None
        for i in lst:
            if i == last:
                continue
            result.append(i)
            last = i
        return result

if __name__ == "__main__":
    Main()