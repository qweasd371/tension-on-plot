from sys import exit
import queue
import threading
import tkinter as tk
from tkinter import filedialog 
from time import time, sleep
from NoCom import NoCom
from MinThreshold import MinThreshold
from functools import partial
try:
    from serial import Serial
    from serial import serialutil
    from serial.tools import list_ports
except ModuleNotFoundError:
    print("Библиотека pyserial не установлена.")
    exit(1)
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
except ModuleNotFoundError:
    print("Библиотека matplotlib не установлена.")
    exit(1)


class Main:
    serial_thread = NoCom()
    result_queue = queue.Queue()
    
    def __init__(self):
        # Списки для хранения данных (значения и время)
        self.list_data_time = []
        self.list_data = []
        self.max_value = 0
        self.file = ""
        
        # Параметры окна и графика
        self.width = 1200
        self.height = 600
        self.size_min_threshold_window = "200x100"
        self.dpi = 100
        self.line_values = []
        
        # Настройки COM порта
        self.serial_port = NoCom()
        self.serial_stop_read_value = False
        self.start_time = float(f"{time():.2f}")
        self.min_threshold_exceeded = False

        # Создание главного окна Tkinter
        self.root = tk.Tk()
        self.min_threshold = MinThreshold(self.root ,self.size_min_threshold_window)
        
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.title("Стропометр")
        
        # Создание меню
        self.menu = tk.Menu(self.root)
        
        # Меню "Файл"
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label="Открыть", command=lambda:(self.ask_path(), self.update_plot()))
        self.file_menu.add_command(label="Сохранить", command=self.save_file)
        self.menu.add_cascade(label="Файл", menu=self.file_menu)

        # Меню "COM порт"
        self.serial_menu = tk.Menu(self.menu, tearoff=False)
        self.serial_setup_menu = tk.Menu(self.serial_menu, tearoff=False)
        
        # Инициализация списка COM портов
        self.list_serial = []
        self.update_list_serial_ports()

        # Добавление команд в меню COM порта
        self.serial_menu.add_command(label=f"Текущий COM порт: {self.serial_port.port}")
        self.serial_menu.add_cascade(label="Установить COM порт", menu=self.serial_setup_menu)
        self.serial_menu.add_command(label="Обновить список портов", command=self.update_list_serial_ports)
        self.serial_menu.add_command(label="Начать читать из COM порта", command=self.serial_start_read)
        self.serial_menu.add_command(label="Остановить чтение из COM порта", command=self.stop)
        self.menu.add_cascade(label="COM порт", menu=self.serial_menu)
        
        self.instruments_menu = tk.Menu(self.menu, tearoff=False)

        # Создание поле ввода минимального порога
        self.instruments_menu.add_command(label="Минимальный порог", command=self.min_threshold.init_window)

        # Создаем кнопку очищения графика
        self.instruments_menu.add_command(label="Очистить график", command=lambda:(self.clear_plot(), self.update_plot()))
        self.menu.add_cascade(label="Инструменты", menu=self.instruments_menu)


        # Создание надпись для отображения максимального значения и значения в данный момент
        self.info_label = tk.Text(self.root, height=2.5, width=self.width)
        self.info_label.tag_config("standard text", font=("Arial", 12))
        self.info_label.tag_config("value", font=("Arial", 30))
        self.info_label.insert(tk.END, "Максимум: ", "standard text")
        self.info_label.insert(tk.END, "0.00", "value")
        self.info_label.insert(tk.END, ", Текущее значение: ", "standard text")
        self.info_label.insert(tk.END, "0.00", "value")
        self.info_label.config(state=tk.DISABLED)
        self.info_label.pack(anchor="nw")

        # Создание графика matplotlib
        self.fig = Figure((self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("F, т")  # Подпись оси Y (нагрузка в тоннах)
        self.ax.set_xlabel("t, с")  # Подпись оси X (время в секундах)
        
        # Создание начальной линии графика
        self.line, = self.ax.plot([], [], "o-")
        self.max_line = self.ax.axhline(0, color="r", label="Максимум: 0,00 т.")
        self.ax.legend()
        
        # Встраивание графика в окно
        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.draw()
        
        # Добавление панели инструментов matplotlib
        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas.get_tk_widget().pack(anchor="nw")

        
        # Добавляем меню на верх
        self.root.config(menu=self.menu)
        self.root.mainloop()
        
        # Завершение работы с COM портом при закрытии приложения
        self.serial_stop_read_value = True
        self.serial_port.close()

    def update_list_serial_ports(self):
        """Метод для обновления списка доступных COM портов и добавления их в меню"""
        # Получение списка доступных портов
        self.list_serial = [i.device for i in list_ports.comports()]
        # И сортируим их
        self.list_serial.sort()
        
        self.serial_setup_menu.destroy()
        self.serial_setup_menu = tk.Menu(self.serial_menu, tearoff=False)
        
        # обновляем меню портов
        for i in self.list_serial:
            self.serial_setup_menu.add_command(label=i, command=partial(self.set_serial_port, i))

        self.serial_menu.entryconfig(1, menu=self.serial_setup_menu)

    def clear_plot(self):
        self.list_data = []
        self.list_data_time = []
        self.max_value = 0

    def update_plot(self):
        self.line.set_data(self.list_data_time, self.list_data)
        self.max_line.set_ydata([self.max_value, self.max_value])

        self.ax.relim()           
        self.ax.autoscale_view()  
        
        # Отрисовка обновленного графика
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        self.update_info_label()

    def update_file(self):
        """Загрузка данных из файла"""
        # Чтение данных из файла
        if self.file_name:
            with open(self.file_name, "r", encoding="utf-8") as file:
                file_data = file.read().splitlines()
                for value in file_data:
                    value = value.split()
                    if float(value[0]) >= self.min_threshold.get_min_threshold() or self.min_threshold_exceeded:
                        self.list_data.append(float(value[0]))      
                        self.list_data_time.append(float(value[1]))
                        self.min_threshold_exceeded = True
                        print(value)
                self.update_plot()
                self.min_threshold_exceeded = False
                file.close()
    
    def ask_path(self): 
        """Открытие диалога выбора файла"""
        self.file_name = filedialog.askopenfilename(
            title="Выберете файл.", 
            filetypes=[("Текстовые файлы.", "*.txt"), 
                       ("Все файлы.", "*.*")]
        )
        if self.file_name:
            self.clear_plot()
            self.update_file()
    
    def save_file(self):
        """Сохранение данных в файл"""
        filename = filedialog.asksaveasfilename(
            title="Выберете файл.", 
            defaultextension=".txt",
            filetypes=[("Текстовые файлы.", "*.txt"),
                       ("Все файлы.", "*.*")]
        )
        if filename:
            with open(filename, "w", encoding="utf-8") as file:
                # Запись данных в формате "значение \t время"
                file.write("\n".join([(f"{self.list_data[i]} \t {self.list_data_time[i]}") 
                                for i in range(len(self.list_data))]) + f"\n{self.max_line.get_ydata()[0]}")
                file.close()

    def stop(self):
        """Остановка чтения данных с COM порта"""
        self.serial_stop_read_value = True
        self.clear_plot()
    
    def update_info_label(self):
        """Обновление метки с максимальным значением"""
        if self.list_data:
            self.max_value = max(map(float, self.list_data))
        else:
            self.max_value = 0
        self.info_label.config(state=tk.NORMAL)
        self.info_label.delete("1.0", tk.END)
        self.info_label.insert(tk.END, "Максимум: ", "standard text")
        self.info_label.insert(tk.END, f"{self.max_value:.2f}", "value")
        self.info_label.insert(tk.END, ", Текущее значение: ", "standard text")
        self.info_label.insert(tk.END, f"{(self.list_data[-1] if self.list_data else 0):.2f}", "value")
        self.info_label.config(state=tk.DISABLED)
        self.max_line.set_label(f"Максимум: {self.max_value} т.")
        self.ax.legend()

    def set_serial_port(self, port):
        """Установка выбранного COM порта"""
        self.serial_port.close()  # Закрытие предыдущего порта
        try:
            # Попытка открытия нового порта
            self.serial_port = Serial(port, self.serial_port.baudrate)
            self.serial_menu.entryconfig(0, label=f"Текущий COM порт: {port}")
        except serialutil.SerialException:
            # Если порт недоступен тогда ставим заглушки
            self.serial_port = NoCom()
            self.serial_menu.entryconfig(0, label=f"Не удалось открыть порт: {port}")

    def serial_read_loop(self, chanchet=False):
        """Основной цикл чтения и отображения данных"""

        # Проверка очереди на наличие новых данных из фонового потока
        try:
            while True:
                val = self.result_queue.get_nowait()
                if val >= self.min_threshold.get_min_threshold() or self.min_threshold_exceeded:
                    self.list_data.append(val)
                    # Добавление времени с момента начала чтения
                    self.list_data_time.append((float(f"{time():.2f}") - self.start_time))
                    chanchet = True  # Флаг обновления графика
                    self.min_threshold_exceeded = True
        except queue.Empty:
            pass  # Если очередь пуста
        
        if chanchet:
            # Обновление данных на графике
            self.update_plot()
            
            if not self.serial_stop_read_value:
                self.root.after(1, self.serial_read_loop)
        else:
            if not self.serial_stop_read_value:
                self.root.after(10, self.serial_read_loop)

    def serial_start_read(self):
        """Начало чтения данных с COM порта"""
        self.min_threshold_exceeded = False

        self.start_time = time()
        self.list_data_time = []  
        self.list_data = []       
        self.serial_stop_read_value = False 
        
        # Запуск фонового потока для чтения данных
        self.serial_thread = threading.Thread(target=self.serial_demon, daemon=True)
        self.serial_thread.start()
        
        # Запуск цикла обновления GUI
        self.root.after(1, self.serial_read_loop)

    def serial_demon(self):
        """Фоновый поток для чтения данных с COM порта"""
        print("Поток чтения запущен")
        while not self.serial_stop_read_value:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline() 
                    if not line: 
                        continue
                    
                    try:
                        line_str = line.decode("ascii").strip()
                        if line_str:
                            value = float(line_str) 
                            self.result_queue.put(value)
                    except ValueError:
                        print(f"Ошибка парсинга числа: {line}")
                    except UnicodeDecodeError:
                        print("Ошибка кодировки")
                else:
                    sleep(0.01)
            except Exception as e:
                print(f"Ошибка в потоке: {e}")
                self.serial_stop_read_value = True
                break
        print("Поток чтения остановлен")

if __name__ == "__main__":
    Main()