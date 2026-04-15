# ==========================
# Web 业务控制层（Controller）
# ==========================

from data.runtime_state import state
from data.session_data import session_mgr
from data.my_sql import *


class WebService:

    # 首页数据
    def get_index_data(self):
        return {
            "weight": state.current_data['weight'],
            "fruit_name": state.current_data['fruit_name'],
            "once_price": state.current_data['once_price'],
            "total_price": state.current_data['total_price']
        }

    # 获取实时数据
    def get_current_data(self):
        with state.lock:
            return state.current_data.copy()

    # 支付操作
    def pay(self, action):
        session = session_mgr.value

        if search_session(session):
            if action == 'confirm':
                edit_transaction_status(session, "Success")
                session_mgr.increment()

            if action == 'cancel':
                edit_transaction_status(session, "Cancel")
                session_mgr.increment()

            state.current_data['total_price'] = 0.0

    # 获取当前 session 商品列表
    def get_session_items(self):
        if not search_session(session_mgr.value):
            return []

        items = search_user_for_s(session_mgr.value)

        return [
            {
                "id": r[0],
                "fruit_name": r[1],
                "weight": r[2],
                "once_price": round(r[3], 2)
            } for r in items
        ]

    # 删除商品
    def delete_item(self, item_id):
        session = session_mgr.value

        del_user_for_id(item_id)
        state.timeout_time, total = write_transaction_data_total(session)
        state.current_data['total_price'] = total
