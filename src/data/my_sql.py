import sqlite3
import time
from datetime import datetime
import config

DB_PATH = config.DB_PATH
# ======== 这部分是数据库的操作，包括插入、查询、删除等 ========#
# ========     以下部分代码是主函数使用的数据库调用   ========#

# 从数据库获取水果价格
def get_fruit_price(class_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT price, name FROM fruit_data WHERE class=?", (int(class_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]      # price, name
    return 0.0, None


# 初始化时查询数据库最后一个session的大小并自动+1
def get_session():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(session) FROM transaction_data;")
    result = cursor.fetchone()[0]
    conn.close()
    return (result or 0) + 1  # 空表时返回 1


# 写数据进入user_data表
def write_user_data(session, class_id, name, weight, once_price):
    sql = """INSERT INTO user_data(session, class, name, weight, once_price, time)
             VALUES (?, ?, ?, ?, ?, ?)"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, (session, int(class_id), name, weight, once_price, time.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()


# 累加查总价
def search_user_for_s_total(session):
    sql = "SELECT COALESCE(SUM(once_price), 0) FROM user_data WHERE session = ?;"
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql, (session,))
        total = cur.fetchone()[0]
        return round(total, 2)  # 保留两位小数


# 更新transaction_data的总价，不存在则直接添加
def write_transaction_data_total(session):
    now_time = datetime.now()
    total = search_user_for_s_total(session)
    time_str = now_time.strftime('%Y-%m-%d %H:%M:%S')  # 使用 now_time 格式化
    sql = """INSERT INTO transaction_data(session, total, time)
             VALUES (?, ?, ?) ON CONFLICT(session) DO \
             UPDATE
             SET total = excluded.total, time = excluded.time;"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, (session, total, time_str))
        conn.commit()
    return now_time, total


# 修改Transaction_Status参数
def edit_transaction_status(session, transaction_status):
    sql = """UPDATE transaction_data
             SET time               = ?,
                 Transaction_Status = ?
             WHERE session = ?;"""
    with sqlite3.connect(DB_PATH, timeout=10) as conn:
        conn.execute(sql, (time.strftime('%Y-%m-%d %H:%M:%S'),
                           transaction_status,
                           session))
        conn.commit()


# 查找session大小，不存在则从返回 1
def search_session(session):
    sql = "SELECT 1 FROM transaction_data WHERE session = ? LIMIT 1;"
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql, (session,))
        return cur.fetchone() is not None


# 查询该session中的所有数据，按照id排序，为后续删除作拓展
def search_user_for_s(session):
    sql = """SELECT id, name, weight, once_price
             FROM user_data
             WHERE session = ?
             ORDER BY id ASC;"""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql, (session,))
        return cur.fetchall()


# 按照id删除user表的那行数据
def del_user_for_id(id):
    sql = "DELETE FROM user_data WHERE id = ?;"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, (id,))
        conn.commit()


# ======== 以下部分代码是登录页面使用的数据库调用 ========#

# 直接查询管理员账号和密码并返回校验
def search_admin():
    sql = "SELECT name, password FROM admin_data LIMIT 1;"
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql).fetchone()
        if cur:
            return cur[0], cur[1]
        else:
            return None, None


# ======== 以下部分代码是管理员页面使用的数据库调用 ========#

# 查询所有水果数据并返回
def all_fruit_data():
    sql = """SELECT class, name, price
             FROM fruit_data
             ORDER BY class ASC;"""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql)
        return cur.fetchall()


# 更新水果价格
def edit_price(class_id, new_price):
    sql = "UPDATE fruit_data SET price = ? WHERE class = ?;"
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, (new_price, class_id))
        conn.commit()


# 后台查询数据（一页50）
def search_transaction_list(page=1, page_size=config.PAGE_SIZE, status='all'):
    offset = (page - 1) * page_size

    if status == 'all':
        sql = """
        SELECT session, total, time, Transaction_Status
        FROM transaction_data
        WHERE total > 0
        ORDER BY time DESC
        LIMIT ? OFFSET ?;
        """
        params = (page_size, offset)
    else:
        sql = """
        SELECT session, total, time, Transaction_Status
        FROM transaction_data
        WHERE Transaction_Status = ? AND total > 0
        ORDER BY time DESC
        LIMIT ? OFFSET ?;
        """
        params = (status, page_size, offset)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall()

# 计算总条数（用于分页）
def count_transaction(status='all'):
    if status == 'all':
        sql = "SELECT COUNT(*) FROM transaction_data WHERE total > 0;"
        params = ()
    else:
        sql = "SELECT COUNT(*) FROM transaction_data WHERE Transaction_Status = ? AND total > 0;"
        params = (status,)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(sql, params)
        return cur.fetchone()[0]