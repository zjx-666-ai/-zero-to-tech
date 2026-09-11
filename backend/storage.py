import sqlite3

DB_FILE = "history.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row      # 让查询结果带上列名（默认是元组）
    return conn
def init_db():                       # 建表、初始化数据库
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        score REAL,
        label TEXT,
        pinyin TEXT,
        created_at TEXT
    )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_history_created ON history(created_at)") # 创建索引
    conn.commit()
    conn.close()


def save_record(record):             # 保存记录到数据库
    conn = get_conn()                 # 获取数据库连接
    cur = conn.cursor()            # 获取游标对象
    cur.execute(                    # 执行SQL语句
        "INSERT INTO history (text, score, label, pinyin, created_at) VALUES (?, ?, ?, ?, ?)",
        [record["text"], record["score"], record["label"], record["pinyin"], record["created_at"]],
    )
    conn.commit()                 # 提交事务
    conn.close()               # 关闭连接


def get_history(limit):            # 获取历史记录
    conn = get_conn()            # 获取数据库连接
    cur = conn.cursor()                 
    rows = cur.execute(           # 执行SQL语句
        "SELECT * FROM history ORDER BY created_at DESC LIMIT ?",
        [limit],
    ).fetchall()               # 获取查询结果
    conn.close()              # 关闭连接

    records = []             # 将查询结果转换为字典列表
    for row in rows:               # 遍历查询结果
        records.append(dict(row))      # 将查询结果转换为字典
    return records            # 返回字典列表

