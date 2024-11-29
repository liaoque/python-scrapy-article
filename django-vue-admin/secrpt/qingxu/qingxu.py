import cls
import dfcf
import weibo
import xueqiu
import sqlite3


def compute():
    conn = sqlite3.connect('qingxu.db')
    # 创建一个Cursor:
    cursor = conn.cursor()

    init(cursor)

    cls.run(cursor)
    dfcf.run(cursor)
    weibo.run(cursor)
    xueqiu.run(cursor)


    # 关闭Cursor:
    cursor.close()

    # 提交事务:
    conn.commit()
    conn.close()

def init(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS m_cls (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, commit TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS m_weibo (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, commit TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS m_xueqiu (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, commit TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS m_dfcf (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, kd_up TEXT, kd_flat TEXT, kd_down TEXT, jg_up TEXT, jg_flat TEXT, jg_down TEXT, cc_up TEXT, cc_flat TEXT, cc_down TEXT,type integer, created_at TEXT)')
    pass


if __name__ == "__main__":
    compute()