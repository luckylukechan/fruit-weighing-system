import threading
import sys
import atexit
import signal
from flask import Flask

# 自定义模块
from data.my_sql import *
from data.session_data import session_mgr
from core.all_hardware import init_hardware, cleanup
from core.weight_engine import WeightEngine
from core.device_service import DeviceService
from web.web_service import WebService
from web.admin_routes import register_admin_routes
from web.web_routes import register_web_routes


# 配置与状态模块
import config

# 设备全局变量
ser = None
cap = None
model = None
# 初始化
stop_event = threading.Event()
web_service = WebService()


app = Flask(__name__)   # Flask Web 服务
app.secret_key = "fruit_system_admin_key"   # 只用于管理员登录
register_web_routes(app)    # 注册购物业务路由
register_admin_routes(app)


def start_hardware():
    global ser, cap, model, serial_queue, camera_queue

    try:
        ser, cap, model = init_hardware(
            camera_no=config.CAMERA_NO,
            serial_port=config.SERIAL_PORT,
            model_path=config.MODEL_PATH,
            test_image=config.TEST_IMAGE
        )
    except Exception as e:
        print(f"硬件初始化失败: {e}")
        sys.exit(1)

    session_mgr.value = get_session()
    print(f"会话获取完成，当前会话:{session_mgr.value}")

    device = DeviceService(ser, cap, stop_event)
    device.start()

    engine = WeightEngine(device.serial_queue, device.camera_queue, model, stop_event)
    threading.Thread(target=engine.run, daemon=True).start()

    print("系统启动完成！等待重量数据...")


def signal_handler(sig, frame):
    print('\n你按下了Ctrl+C！正在关闭服务器...')
    stop_event.set()
    time.sleep(0.5)
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    start_hardware()
    atexit.register(cleanup)

    app.run(host='127.0.0.1', port=5000, debug=False)
