# 全局session，模块化便于管理，且防止线程冲突
import threading

class Session:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    @property   # 只读，便于直接用方法名访问方法
    def value(self):
        with self._lock:
            return self._value

    @value.setter   # 对value值进行写的操作（也是不用加括号）
    def value(self, new_value: int):
        with self._lock:
            self._value = new_value

    def increment(self):
        """原子自增，返回新值"""
        with self._lock:
            self._value += 1
            return self._value

# 全局唯一实例
session_mgr = Session()