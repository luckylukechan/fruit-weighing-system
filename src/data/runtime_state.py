# ======================
# 运行时状态管理
# ======================

import threading

class RuntimeState:
    def __init__(self):
        # 业务状态
        self.weight_count = 0
        self.weight_state = True
        self.last_weight = None
        self.timeout_time = None

        # 页面显示数据
        self.current_data = {
            'weight': 0,
            'fruit_name': '',
            'once_price': 0.0,
            'total_price': 0.0
        }

        # 线程锁
        self.lock = threading.Lock()


# 全局唯一状态实例
state = RuntimeState()
