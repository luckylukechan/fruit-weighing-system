# 硬件初始化封装模块
import cv2
import time
from ultralytics import YOLO
import serial

# 内部提前初始化
_ser = None
_cap = None
_model = None

def init_hardware(camera_no, serial_port, model_path, test_image):
    ser = None
    global _ser, _cap, _model
    for i in range(3):
        try:
            ser = serial.Serial(serial_port, 115200, timeout=1)
            print("串口初始化完成")
            break
        except Exception as e:
            print(f"尝试打开串口失败 ({i + 1}/3): {e}")
            if ser:
                try:
                    ser.close()
                except:
                    pass
                ser = None
            time.sleep(1)
    else:
        if ser:
            try:
                ser.close()
            except:
                pass
        raise Exception("无法打开串口，重试3次后失败")

    # 初始化摄像头
    cap = cv2.VideoCapture(camera_no)
    if not cap.isOpened():
        time.sleep(0.5)
        cap = cv2.VideoCapture(camera_no)
        if not cap.isOpened():
            cap.release()
            raise Exception(f"摄像头初始化失败 (设备号: {camera_no})")

    ret, frame = cap.read()
    if not ret:
        cap.release()
        raise Exception("摄像头初始化后读取失败，请检查摄像头连接")

    # 加载并预热模型
    model = YOLO(model_path, task="detect")
    model(test_image, conf=0.5, verbose=False)  # 预热
    print("模型加载完成")

    _ser, _cap, _model = ser, cap, model
    return ser, cap, model

# 安全释放串口、摄像头
def cleanup():
    global _ser, _cap
    print('系统关闭中 …')

    if _ser and _ser.is_open:
        try:
            _ser.close()
            print('串口已安全释放')
        except:
            pass
        finally:
            _ser = None

    if _cap and _cap.isOpened():
        try:
            _cap.release()
            print('摄像头已安全释放')
        except:
            pass
        finally:
            _cap = None

    cv2.destroyAllWindows()
