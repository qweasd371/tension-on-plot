import serial
import threading
import queue
class Serial():
    def __init__(self, port: str, baudrate: int = 9600, timeout: bool | None = None):
        self.baudrate = baudrate
        self.timeout = timeout
        #self.result_queue = queue.Queue()
        self.port = serial.Serial(port, self.baudrate, timeout=self.timeout)

    def close(self):
        self.port.close()
        """
    def read(self) -> str:
        threading.Thread(target=self._read, args=(self.result_queue, self.port), daemon=True).start()
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def _read(_, q: queue.Queue, com: serial.Serial):
        result = com.readline().decode("ascii").strip()
        q.put(result)
    
    def read_non_start(self):
        return threading.Thread(target=self._read, args=(self.result_queue, self.port), daemon=True), self.result_queue

"""