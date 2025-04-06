import time
import threading

class Snowflake64:
    def __init__(self, machine_id: int):
        if machine_id >= 1024 or machine_id < 0:
            raise ValueError("Machine ID must be in [0, 1023]")
        
        self.machine_id = machine_id
        self.epoch = 1735689600000  # Custom epoch: Jan 1, 2025 (in ms)
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _current_millis(self):
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_ts):
        ts = self._current_millis()
        while ts <= last_ts:
            ts = self._current_millis()
        return ts

    def generate(self):
        with self.lock:
            ts = self._current_millis()

            if ts == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
                if self.sequence == 0:
                    ts = self._wait_next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = ts
            id = ((ts - self.epoch) << 22) | (self.machine_id << 12) | self.sequence
            return id
        
gen = Snowflake64(machine_id=1)
unique_id = gen.generate()
print(unique_id)