import sys
import tkinter as tk
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
except:
    print("Библиотека matplotlib не установлена.")
    sys.exit(1)

class Main():
    def __init__(self, list_data: list = [], 
                 file_name: str = "",
                 width: int = 600, height: int = 800,
                 dpi: int = 100,
                 time: int | float = 0.5):
        
        self.list_data = list_data
        self.file_name = file_name
        self.width = width
        self.height = height
        self.dpi = dpi
        self.time = int(time * 1000)
        self.line_values = []


        self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")

        self.info_lable = tk.Label(self.root, text="""Средне статистическое: 0.0000
Средне статистическое (без учёта нулей): 0.0000
Максимальное значение: 0.0000""")
        self.info_lable.pack()

        self.file_name_entry = tk.Entry(self.root)
        self.file_name_entry.pack()
        self._focus_out_file_name_entry()
        self.file_name_entry.bind("<Return>", self.update_file_name)
        self.file_name_entry.bind("<FocusIn>", self._focus_in_file_name_entry)
        self.file_name_entry.bind("<FocusOut>", self._focus_out_file_name_entry)

        self.load_file_button = tk.Button(self.root, text="Загрузить файл", command=self.load_file)
        self.load_file_button.pack()

        self.stop_button = tk.Button(self.root, text="Завершить отрисовку", command=self.stop)
        self.stop_button.pack()
        
        self.fig = Figure((self.width / self.dpi, self.height / self.dpi), dpi=self.dpi)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot(range(len(self.list_data)), self.list_data)

        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.draw()

        toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        toolbar.update()
        self.canvas.get_tk_widget().pack(anchor="e")
        
        self.root.mainloop()

    def load_file(self):
        with open(self.file_name, "r", encoding="utf-8") as file:
            self.line_values = [float(i) for i in file.read().splitlines() if i.strip()]
            self.ax.clear()
            self.line, = self.ax.plot([], [])
            self.list_data = []
            self._add_step_for_line()
            file.close()
        

    def _add_step_for_line(self):
        if self.line_values:
            self.update_info_label()

            self.list_data.append(self.line_values.pop(0))

            self.line.set_data(range(len(self.list_data)), self.list_data)
            self.ax.relim()
            self.ax.autoscale_view()

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.root.after(self.time, self._add_step_for_line)
    
    def stop(self):
        self.line_values = []
    
    def update_info_label(self, *argv):
        self.info_lable.config(text=f"""Средне статистическое: {self.mean(self.list_data):.4f}
Средне статистическое (без учёта нулей): {self.mean(self.list_data, True):.4f}
Максимальное значение: {max(self.list_data) if self.list_data else 0:.4f}""")
    
    def update_file_name(self, *argv):
        self.file_name = self.file_name_entry.get()

    def _focus_in_file_name_entry(self, *argv):
        if self.file_name_entry.get().split() == "Введите название фаила.":
            self.file_name_entry.delete(0, tk.END)
    
    def _focus_out_file_name_entry(self, *argv):
        if not self.file_name_entry.get().split():
            self.file_name_entry.delete(0, tk.END)
            self.file_name_entry.insert(tk.END, "Введите название фаила.")

    @staticmethod
    def mean(list_data, without_zero: bool = False):
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