import sys
import threading
import tkinter as tk
from tkinter import filedialog 
from serial import serialutil
import time
import queue
from functools import partial
try:
    import serial
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

class NoCom():
    def __init__(self):
        self.port = "выберите порт"
        self.baudrate = 9600
        self.in_waiting = 0
    def close(self):
        pass
    def readline(self):
        return 0 

class Main():
    serial_thread = None
    result_queue = queue.Queue()
    def __init__(self):
        self.list_data_time = []
        self.list_data = []
        self.file = ""
        self.width = 1200
        self.height = 600
        self.dpi = 100
        self.line_values = []
        self.serial_port = NoCom()
        self.serial_stop_read_value = False

        self.start_time = time.time()

        # Создание окна
        self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")

        self.menu = tk.Menu(self.root)
        
        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label="Открыть", command=self.ask_path)
        self.file_menu.add_command(label="Перезагрузить файл", command=self.update_file)
        self.file_menu.add_command(label="Сохранить файл", command=self.save_file)

        self.menu.add_cascade(label="Файл", menu=self.file_menu)

        self.serial_menu = tk.Menu(self.menu, tearoff=False)
        self.serial_setup_menu = tk.Menu(self.serial_menu, tearoff=False)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                

        self.list_serial = []
        self.update_list_serial_ports()

        self.serial_menu.add_command(label=f"Текущий COM порт: {self.serial_port.port}")
        self.serial_menu.add_cascade(label="Установить COM порт", menu=self.serial_setup_menu)
        self.serial_menu.add_command(label="Обновить список портов", command=self.update_list_serial_ports)
        self.serial_menu.add_command(label="Начать читать из COM порта", command=self.serial_start_read)

        self.menu.add_cascade(label="COM порт", menu=self.serial_menu)

        self.menu.add_command(label="Стоп", command=self.stop)

        # Инициализируем график
        self.fig = Figure((self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylabel("m, т")
        self.ax.set_xlabel("t, мс")
        self.line, = self.ax.plot(range(len(self.list_data)), self.list_data, "o-")

        # Создаём надпись для вывода максимального значения
        self.info_label = tk.Label(self.root, text="Максимальное значение: 0.00")
        self.info_label.pack(anchor="nw")

        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas.get_tk_widget().pack(anchor="nw")
        
        # Зацикливаем
        self.root.config(menu=self.menu)
        self.root.mainloop()
        self.serial_stop_read_value = True
        self.serial_port.close()

    def update_list_serial_ports(self):
        self.list_serial = [i.device for i in list_ports.comports()]
        self.list_serial.sort()
        self.serial_setup_menu.destroy()
        self.serial_setup_menu = tk.Menu(self.serial_menu, tearoff=False)    
        for i in self.list_serial:
            self.serial_setup_menu.add_command(label=i, command=partial(self.set_serial_port, i))
        self.serial_menu.entryconfig(1, menu=self.serial_setup_menu)

    def update_file(self):
        self.list_data = []
        self.list_data_time = []
        self.stop()
        with open(self.file_name, "r", encoding="utf-8") as file:
            for value in file.read().splitlines():
                value = value.split()
                self.list_data.append(value[0])
                self.list_data_time.append(value[1])
                self.serial_read_loop(chanchet=True)
            file.close()
        
    def ask_path(self): 
        self.file_name = filedialog.askopenfilename(title="Выберете файл.", filetypes=[("Текстовые файлы.", "*.txt"),
                                                                                        ("Все файлы.", "*.*")])
        self.update_file()
    
    def save_file(self):
        file = filedialog.asksaveasfile(title="Выберете файл.", filetypes=[("Текстовые файлы.", "*.txt")])
        file.write("\n".join([(f"{self.list_data[i]} \t {self.list_data_time[i]}") for i in range(len(self.list_data))]))
        file.close()

    def stop(self):
        self.serial_stop_read_value = True
    
    def update_info_label(self, *argv):
        self.info_label.config(text=f"Максимальное значение: {max(map(float, self.list_data)) if self.list_data else 0:.2f}")

    def set_serial_port(self, port):
        self.serial_port.close()
        try:
            self.serial_port = serial.Serial(port, self.serial_port.baudrate)
            self.serial_menu.entryconfig(0, label=f"Текущий COM порт: {port}")
        except serialutil.SerialException:
            self.serial_port = NoCom()
            self.serial_menu.entryconfig(0, label=f"Не удалось открыть порт: {port}")

    def serial_read_loop(self, chanchet=False):
        self.update_info_label()

        try:
            while True:
                val = self.result_queue.get_nowait()
                self.list_data.append(val[0])
                self.list_data_time.append(val[1])
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
        else:
            if not self.serial_stop_read_value:
                self.root.after(10, self.serial_read_loop)


    def serial_start_read(self):
        self.list_data_time = []
        self.list_data = []

        self.serial_stop_read_value = False
        
        self.serial_thread = threading.Thread(target=self.serial_demon, daemon=True)
        self.serial_thread.start()
        
        self.root.after(1, self.serial_read_loop)
    
    def serial_stop_read(self):
        self.serial_stop_read_value = True

    def serial_demon(self):
        """Фоновый поток чтения данных"""
        print("Поток чтения запущен")
        last = 0
        while not self.serial_stop_read_value:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline() 
                    if not line: continue
                    
                    try:
                        line_str = line.decode("ascii").strip()
                        if line_str and line_str != last:
                            value = float(line_str)
                            last = line_str
                            self.result_queue.put((value, float((time.time() - self.start_time))))
                    except ValueError:
                        print(f"Ошибка парсинга числа: {line}")
                    except UnicodeDecodeError:
                        print("Ошибка кодировки")
                else:
                    time.sleep(0.01) # Не грузим CPU, если данных нет
            except Exception as e:
                print(f"Ошибка в потоке: {e}")
                self.serial_stop_read_value = True
                break
        print("Поток чтения остановлен")

            

if __name__ == "__main__":
    main_app = Main()