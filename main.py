import sys
import threading
import tkinter as tk
from tkinter import filedialog 
from serial import serialutil
import time
import queue
from functools import partial
try:
    import Serial
    from serial.tools import list_ports
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
    serial_thread = None
    result_queue = queue.Queue()
    def __init__(self, list_data: list = [0],
                 file: str = "",
                 serial_port: tuple[str, int, bool | None] = [],
                 width: int = 600, height: int = 600,
                 dpi: int = 100,
                 #time: int | float = 0.001,
                 min_threshold: float = 0.5):
        self.list_data_time = [0]
        self.list_data = list_data
        self.file = file
        self.width = width
        self.height = height
        self.dpi = dpi
        #self.time = int(time * 1000)
        self.line_values = []
        self.min_threshold = min_threshold
        self.serial_port = Serial.Serial(*serial_port)
        # Создание окна
        self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")

        self.menu = tk.Menu(self.root)

        # Создаём меню графика
        self.plot_menu = tk.Menu(self.menu, tearoff=False)
        # Создаём кнопку начатие отрисовки
        self.plot_menu.add_command(label="Начать отрисовку", command=self.start)
        # Создаём кнопку завершение отрисовки
        self.plot_menu.add_command(label="Завершить отрисовку", command=self.stop)

        self.menu.add_cascade(label="График", menu=self.plot_menu)
        
        self.is_file_use = tk.BooleanVar(value=True)

        # Создаём меню фаила
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        # Создаем кнопку для переключение режима с Com порта на файл
        self.file_menu.add_radiobutton(label="Использовать файл", variable=self.is_file_use, value=True, command=self.update_serial_and_file_menu)
        # Создаем кнопку "Обзор"
        self.file_menu.add_command(label="Обзор", command=self.ask_path)
        # Создаём кнопку для загрузки файла
        self.file_menu.add_command(label="Перезагрузить файл", command=self.update_file)

        self.menu.add_cascade(label="Файл", menu=self.file_menu)

        self.serial_menu = tk.Menu(self.menu, tearoff=False)
        self.serial_setup_menu = tk.Menu(self.serial_menu,tearoff=False)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                

        self.list_serial = [i.device for i in list_ports.comports()]
        self.list_serial.sort()

        for i in self.list_serial:
            self.serial_setup_menu.add_command(label=i, command=partial(self.set_serial_port, i))

        self.serial_menu.add_radiobutton(label="Использовать COM порт", variable=self.is_file_use, value=False, command=self.update_serial_and_file_menu)
        self.serial_menu.add_cascade(label="Установить COM порт", menu=self.serial_setup_menu)
        self.serial_menu.add_command(label=f"Текущий COM порт: {self.serial_port.port.port}")
        self.serial_menu.add_command(label="Начать читать из COM порта", command=self.serial_start_read)
        self.serial_menu.add_command(label="Остановить чтение из COM порта", command=self.serial_stop_read)
        
        self.serial_stop_read_value = False

        self.menu.add_cascade(label="COM порт", menu=self.serial_menu)
        self.update_serial_and_file_menu()

        # Инициализируем график
        self.fig = Figure((self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("m, т")
        self.ax.set_xlabel("t, мс")
        self.line, = self.ax.plot(range(len(self.list_data)), self.list_data, "o-")

        # Создаём надпись для вывода максимального значения
        self.info_label = tk.Label(self.root, text="Максимальное значение: 0.0000")
        self.info_label.pack(anchor="nw")

        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas.get_tk_widget().pack(anchor="nw")
        
        # Зацикливаем
        self.root.config(menu=self.menu)
        self.root.mainloop()
        self.serial_port.close()

    def clear_plot(self):
        "Очищает график"
        # Очиняем и обновляем график
        self.list_data = []
        self.ax.clear()
        self.line, = self.ax.plot([], [], "o-")

        # Ставим названия сторон
        self.ax.set_ylabel("m, т")
        self.ax.set_xlabel("t, мс")

    def update_file(self):
        "Загрузка фаила."
        with open(self.file_name, "r", encoding="utf-8") as file:
            self.line_values = []
            for line_value in file.read().splitlines():
                line_value = line_value[:line_value.rfind("]")][:line_value.find("[")]
                if line_value and float(line_value) >= self.min_threshold:
                    self.line_values.append(float(line_value))
            # Закрываем файл
            file.close()
        
    def ask_path(self): 
        "Обзор фаилов."
        self.file_name = filedialog.askopenfilename(title="Выберете файл.", filetypes=[("Текстовые файлы.", "*.txt"),
                                                                                        ("Все файлы.", "*.*")])
        self.update_file()

    def start(self):
        self.clear_plot()
        if self.line_values:
            self.add_step_for_line()

    def add_step_for_line(self):
        "Шаг отрисовки."
        # Обновление информациональных надписей
        

    def stop(self):
        "Остановка отрисовки."
        self.line_values = []
        self.serial_stop_read_value = False
    
    def update_info_label(self, *argv):
        "Обновление информационной надписи."
        self.info_label.config(text=f"Максимальное значение: {max(map(float, self.list_data)) if self.list_data else 0:.4f}")

    def set_serial_port(self, port):
        self.serial_port.close()
        serial_port = self.serial_port.port.port
        try:
            self.serial_port = Serial.Serial(port, self.serial_port.baudrate, self.serial_port.timeout)
            self.serial_menu.entryconfig(2, label=f"Текущий COM порт: {port}")
        except serialutil.SerialException:
            self.serial_port = Serial.Serial(serial_port, self.serial_port.baudrate, self.serial_port.timeout)
            self.serial_menu.entryconfig(2, label=f"Не удалось открыть порт: {port}")

    def update_serial_and_file_menu(self):
        end_index_file_menu = self.file_menu.index("end")
        end_index_serial_menu = self.serial_menu.index("end")
        if self.is_file_use.get():
            for i in range(1, end_index_file_menu + 1):
                self.file_menu.entryconfig(i, state=tk.ACTIVE)

            for i in range(1, end_index_serial_menu + 1):
                self.serial_menu.entryconfig(i, state=tk.DISABLED)
        else:
            for i in range(1, end_index_file_menu + 1):
                self.file_menu.entryconfig(i, state=tk.DISABLED)

            for i in range(1, end_index_serial_menu + 1):
                self.serial_menu.entryconfig(i, state=tk.ACTIVE)

    def serial_read_loop(self):
        self.update_info_label()
        chanchet = False

        try:
            while True:
                val = self.result_queue.get_nowait()
                self.list_data.append(val)
                self.list_data_time.append(len(self.list_data_time))
                chanchet = True
        except queue.Empty:
            pass
        
        if chanchet:
            # Обновляет данные
            self.line.set_data(self.list_data_time, self.list_data)
            self.ax.relim()
            self.ax.autoscale_view()

            # Отрисовка графика
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        if not self.serial_stop_read_value:
            self.root.after(1, self.serial_read_loop)

    def serial_start_read(self):

        if self.serial_thread is None:
            self.serial_thread = threading.Thread(target=self.serial_demon, daemon=True)
            self.serial_thread.start()

        if not self.serial_stop_read_value:
            self.root.after(0, self.serial_read_loop)

        else:
            self.serial_thread.join()
            self.serial_stop_read_value = False
            self.serial_thread = threading.Thread(target=self.serial_demon, daemon=True)
            self.serial_thread.start()
    
    def serial_stop_read(self):
        self.serial_stop_read_value = True

    def serial_demon(self):
        while not self.serial_stop_read_value:
            try:
                value = self.serial_port.port.readline().decode("ascii").strip()
                if value:
                    self.result_queue.put(value)
            except UnicodeDecodeError:
                pass

            

if __name__ == "__main__":
    Main(serial_port=("COM1", 9600, 0.1))