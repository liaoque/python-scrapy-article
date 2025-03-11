

def init(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_cls (id integer NOT NULL PRIMARY KEY AUTOINCREMENT, tid TEXT, content TEXT, created_at TEXT, type integer, `commited` TEXT)')

    pass


def query(cursor, d, code):
    cursor.execute('SELECT tid FROM m_cls WHERE type=? order by id desc limit 1', (type,))
    return cursor.fetchone()


def update(cursor, id, vix):
    cursor.execute('SELECT tid FROM m_cls WHERE type=? order by id desc limit 1', (type,))
    values = cursor.fetchone()
    if len(values) == 0:
        return 0
    return 1


def insert(cursor, code, d, vix):
    cursor.execute('SELECT tid FROM m_cls WHERE type=? order by id desc limit 1', (type,))
    values = cursor.fetchone()
    if len(values) == 0:
        return 0
    return 1
