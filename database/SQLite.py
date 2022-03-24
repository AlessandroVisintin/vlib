import sqlite3
from pathlib import Path


class SQLite:
    
    
    def __init__(self, srv_path='.', db_name='database.db'):
        Path(srv_path).mkdir(parents=True, exist_ok=True)
        self.path = f'{srv_path}/{db_name}'
        self.conn = sqlite3.connect(self.path)


    def __del__(self):
        self.conn.close()


    def _tables(self):
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        print(self.conn.execute(query).fetchall())
    
    
    def _schema(self, name):
        query = f"SELECT sql FROM sqlite_schema WHERE name = '{name}';"
        print(self.conn.execute(query).fetchall())


    def _size(self, name, index='id'):
        crs = self.conn.cursor()
        crs.execute(f'SELECT COUNT({index}) FROM {name};')
        print(crs.fetchall())


    def _query(self, query, fetch=True):
        crs = self.conn.cursor()
        crs.execute(query)
        if fetch:
            return crs.fetchall()
        return crs


    def create_table(self, name, cols, key=None):
        query = (
            f'CREATE TABLE IF NOT EXISTS {name} ('
                f'{", ".join([" ".join(col) for col in cols])}'
                f'{", PRIMARY KEY (" + ",".join(key) + ")" if key else ""}'
            ');'
        )
        return self._query(query, fetch=False)
    
    
    def insert_rows(self, name, rows, replace=True, commit=True):
        if len(rows) == 0:
            return None
        query = (
            f'INSERT {"OR REPLACE " if replace else "OR IGNORE "}'
            f'INTO {name} VALUES ({",".join(["?"]*len(rows[0]))});'
        )
        crs = self.conn.cursor()        
        for row in rows:
            crs.execute(query, row)
        if commit:
            self.conn.commit()
        return crs


    def get(self, name, **kwargs):
        query = (
            f'SELECT {", ".join(kwargs["cols"]) if "cols" in kwargs else "*"} '
            f'FROM {name}'
            f'{" "+" ".join(kwargs["filters"]) if "filters" in kwargs else ""};'
        )
        return self._query(query)
        