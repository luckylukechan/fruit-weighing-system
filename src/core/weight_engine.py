# ==========================
# 称重识别业务引擎
# ==========================
import config
from data.runtime_state import state
from data.session_data import session_mgr
from data.my_sql import *
from datetime import timedelta


class WeightEngine:

    def __init__(self, serial_queue, camera_queue, model, stop_event):
        self.serial_queue = serial_queue
        self.camera_queue = camera_queue
        self.model = model
        self.stop_event = stop_event

    def run(self):
        """主业务循环（原 main_loop 完整迁移）"""
        while not self.stop_event.is_set():

            # 超时自动结算
            if state.timeout_time is not None:
                if datetime.now() - state.timeout_time > timedelta(seconds=config.TIMEOUT_SECONDS):
                    session_mgr.increment()
                    state.timeout_time = None
                    state.current_data['total_price'] = 0.0

            if not self.serial_queue.empty():
                weight = int(self.serial_queue.get())

                with state.lock:
                    state.current_data['weight'] = weight

                # 如果处于锁定状态，仅更新重量
                if not state.weight_state:
                    if weight <= config.WEIGHT_THRESHOLD:
                        state.weight_state = True
                        state.weight_count = 0
                        state.last_weight = None
                        state.current_data['fruit_name'] = ""
                        state.current_data['once_price'] = 0.0
                    continue

                # 进入识别流程
                if weight > config.WEIGHT_THRESHOLD:
                    if state.last_weight == weight:
                        state.weight_count += 1
                    else:
                        state.last_weight = weight
                        state.weight_count = 1

                    if state.weight_count > config.SAME_WEIGHT_TIMES:
                        frames = []
                        while not self.camera_queue.empty() and len(frames) < 3:
                            frames.append(self.camera_queue.get())

                        if len(frames) == 3:
                            total_cls_counts = {}

                            for frame in frames:
                                results = self.model(frame, conf=0.5, verbose=False)
                                r = results[0]

                                cls_array = r.boxes.cls.cpu().numpy().astype(int)
                                for cls_id in cls_array:
                                    total_cls_counts[cls_id] = total_cls_counts.get(cls_id, 0) + 1

                            if total_cls_counts:
                                max_count = int(max(total_cls_counts, key=total_cls_counts.get))
                                price, name = get_fruit_price(max_count)
                                once_price = round((weight * price / 1000), 2)

                                write_user_data(session_mgr.value, max_count, name, weight, once_price)
                                state.timeout_time, _ = write_transaction_data_total(session_mgr.value)

                                with state.lock:
                                    state.current_data['fruit_name'] = name
                                    state.current_data['once_price'] = once_price
                                    state.current_data['total_price'] = search_user_for_s_total(session_mgr.value)
                            else:
                                with state.lock:
                                    state.current_data['fruit_name'] = "unknown"
                                    state.current_data['once_price'] = 0.0

                        state.weight_state = False
                        state.weight_count = 0
                        state.last_weight = None
                else:
                    state.weight_count = 0
                    state.last_weight = None

            time.sleep(0.01)
