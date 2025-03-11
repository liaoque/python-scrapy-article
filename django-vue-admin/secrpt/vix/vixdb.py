

def init(cursor):
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS m_vix ('
        'id integer NOT NULL PRIMARY KEY AUTOINCREMENT,'
        ' code TEXT, vix TEXT, created_at TEXT)')

    pass


def query(cursor, d, code):
    cursor.execute('SELECT id FROM m_vix WHERE code=? and created_at=? limit 1', (code,d))
    return cursor.fetchone()


def update(cursor, id, vix):
    cursor.execute('update m_vix set vix=? WHERE id=? order by id desc limit 1', (vix, id))


def insert(cursor, code, d, vix):
    cursor.execute('insert into m_vix (code, vix, created_at) VALUES (?, ?, ?)', (code, d, vix,))
