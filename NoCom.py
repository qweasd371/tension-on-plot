class NoCom:
    "Класс для эмуляции COM порта." 
    def __init__(self):
        self.port = "выберите порт"
        self.baudrate = 9600
        self.in_waiting = 0
    def close(self):
        return
    def readline(self):
        return 0 
    def join(self):
        return