from data.my_sql import search_admin, all_fruit_data, edit_price    # 编辑价格
from data.my_sql import search_transaction_list, count_transaction, search_user_for_s  # 查看数据
import config

class AdminService:
    def verify_login(self, username, password):
        db_user, db_pass = search_admin()
        if not db_user:
            return False, "管理员账户未配置"

        if username == db_user and password == db_pass:
            return True, None
        else:
            return False, "用户名或密码错误"


    def get_all_fruits(self):
        rows = all_fruit_data()
        fruits = []
        for row in rows:
            fruits.append({
                "class": row[0],
                "name": row[1],
                "price": row[2]
            })
        return fruits


    def update_price(self, class_id, new_price):
        edit_price(class_id, new_price)


    # 交易列表封装
    def get_transaction_list(self, page, status):
        rows = search_transaction_list(page, config.PAGE_SIZE, status)
        total = count_transaction(status)

        data = []
        for row in rows:
            data.append({
                "session": row[0],
                "total": row[1],
                "time": row[2],
                "status": row[3]
            })

        return data, total


    # 单次交易详情
    def get_session_detail(self, session_id):
        rows = search_user_for_s(session_id)

        details = []
        for r in rows:
            details.append({
                "id": r[0],
                "name": r[1],
                "weight": r[2],
                "price": r[3]
            })

        return details