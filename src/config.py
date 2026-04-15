# 系统配置文件
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 路径配置
MODEL_PATH = os.path.join(DATA_DIR, r"best.pt")
TEST_IMAGE = os.path.join(DATA_DIR, "test.jpg")
DB_PATH = os.path.join(DATA_DIR, "datas.db")

# 硬件设备编号管理
CAMERA_NO = 0
SERIAL_PORT = "COM3"

# 业务参数
SAME_WEIGHT_TIMES = 3   # 称重时相同重量次数
WEIGHT_THRESHOLD = 25   # 重量阈值（超过或恢复才开始后续称重）
TIMEOUT_SECONDS = 60    # 超时时间
PAGE_SIZE = 10          # 数据显示界面一页显示数量
