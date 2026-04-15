# ==========================
# 设备服务层（串口 + 相机）
# ==========================

import queue
import threading
import time


class DeviceService:

    def __init__(self, ser, cap, stop_event):
        self.ser = ser
        self.cap = cap
        self.stop_event = stop_event

        self.serial_queue = queue.Queue(maxsize=10)
        self.camera_queue = queue.Queue(maxsize=3)

    # ======================
    # 串口读取线程
    # ======================
    def serial_reader(self):
        while not self.stop_event.is_set():
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line.lstrip('-').isdigit():
                    self.serial_queue.put(line)
            except (OSError, self.ser.SerialException):
                break
            except Exception as e:
                if not self.stop_event.is_set():
                    print(f"串口错误: {e}")
                time.sleep(0.1)

    # ======================
    # 相机读取线程
    # ======================
    def camera_reader(self):
        while not self.stop_event.is_set():
            if self.cap is None:
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if ret:
                if self.camera_queue.full():
                    self.camera_queue.get()
                self.camera_queue.put(frame)
            else:
                time.sleep(0.01)

    # ======================
    # 启动所有设备线程
    # ======================
    def start(self):
        threading.Thread(target=self.serial_reader, name="SerialReader", daemon=True).start()
        threading.Thread(target=self.camera_reader, name="CameraReader", daemon=True).start()

        print("设备服务启动完成（串口 + 相机线程已运行）")
