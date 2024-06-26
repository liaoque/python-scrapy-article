import sqlite3
import pandas as pd


class DClient:
    conn = None

    def __init__(self):
        self.conn = sqlite3.connect('stock.db')

    def save(self, df, table_name):
        return df.to_sql(table_name, self.conn, if_exists='replace', index=False)

    def select(self, sql):
        return pd.read_sql_query(sql, self.conn)
