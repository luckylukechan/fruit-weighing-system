import sqlite3

# 创建并连接数据库
conn = sqlite3.connect('./datas.db')
cursor = conn.cursor()

# 创建 fruit_data 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS fruit_data (
    class INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
''')

# 创建 user_data 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session INTEGER NOT NULL,
    class INTEGER NOT NULL,
    name TEXT NOT NULL,
    weight REAL NOT NULL,
    once_price REAL NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (class) REFERENCES fruit_data(class)
)
''')

# 创建 transaction_data 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS transaction_data (
    session INTEGER PRIMARY KEY,
    total REAL NOT NULL,
    time TEXT NOT NULL,
    Transaction_Status TEXT NOT NULL DEFAULT 'Timeout' 
)
''')

# 创建 admin_data 表
cursor.execute('''
CREATE TABLE IF NOT EXISTS admin_data (
    name TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

# 插入初始数据到 fruit_data 表 (水果类别与价格)
fruits = [
    (0, '苹果', 1.0),
    (1, '杨桃', 2.0),
    (2, '火龙果', 3.0),
    (3, '葡萄', 4.0),
    (4, '橘子', 5.0),
    (5, '桃子', 6.0),
    (6, '梨', 7.0),
    (7, '凤梨', 8.0),
    (8, '草莓', 9.0),
    (9, '西红柿', 10.0),
    (10, '西瓜', 11.0),
]

cursor.executemany('''
INSERT OR REPLACE INTO fruit_data (class, name, price)
VALUES (?, ?, ?)
''', fruits)

# 插入管理员数据
admin_data = ('admin', '000000')  # 初始管理员用户名和密码（明文）
cursor.execute('''
INSERT OR REPLACE INTO admin_data (name, password)
VALUES (?, ?)
''', admin_data)

# 提交并关闭数据库连接
conn.commit()
conn.close()

print("Database 'datas.db' initialized successfully.")
