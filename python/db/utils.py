import sqlite3
from datetime import datetime

class DB:
    """
        DB helper class
    """
    DB_PATH = None

    def __init__ (self):
        pass

    def cdt():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def commit (query,values=()):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute(query,values)
        conn.commit()
        conn.close()


    @staticmethod
    def select (query,values=()):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute(query,values)
        rows = cur.fetchall()
        for row in rows:
            yield row
        conn.commit()
        conn.close()

    @staticmethod
    def reset ():
        os.remove(DB.DB_PATH)
        stat_db(None)

    @staticmethod
    def stat_db (sqlite_bootstrap):
        if sqlite_bootstrap == None:
            sqlite_bootstrap = input (f"Please put in the path to your SQLite DB [enter for current PWD: {os.getcwd()}]")
        if sqlite_bootstrap == "":
            sqlite_bootstrap = os.getcwd();

        DB.DB_PATH = sqlite_bootstrap + "/core.sqlite";
        try:
            os.stat(sqlite_path)
        except Exception:
            DB.build_database(sqlite_bootstrap)

    @staticmethod
    def build_database(path):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS goals")
        cur.execute("DROP TABLE IF EXISTS stimuli")
        cur.execute("DROP TABLE IF EXISTS response")
        cur.execute("DROP TABLE IF EXISTS memories")
        cur.execute("DROP TABLE IF EXISTS memory_lookup")
        cur.execute("DROP TABLE IF EXISTS xpert_results")
        cur.execute("DROP TABLE IF EXISTS last_boiler")
        cur.execute("DROP TABLE IF EXISTS thoughts")
        cur.execute("DROP TABLE IF EXISTS preferences")
        cur.execute('''
                    create table preferences (
                    pid integer primary key,
                    key text not null,
                    value text not null
                    )''')
        cur.execute('''
                    create table stimuli (
                    sid integer primary key,
                    timestamp text not null,
                    prompt text not null
                    )''')

        cur.execute('''
                    create table response (
                    rid integer primary key,
                    sid integer unique,
                    timestamp text not null,
                    response text not null,
                    think text not null
                    )''')
                    
        cur.execute('''
                    create table goals (
                    gid integer primary key,
                    progress float not null,
                    timestamp text not null,
                    description text not null
                    )''')

        cur.execute('''
                    create table memories (
                    mid integer primary key,
                    description text not null,
                    timestamp text not null
                    )''')

        cur.execute('''
                    create table memory_lookup (
                    mid integer not null,
                    sid integer not null
                    )''')

        cur.execute('''
                    create table xpert_results (
                    xid integer primary key,
                    command text not null,
                    result text not null,
                    timestamp text not null
                    )''')

        cur.execute('''
                    create table last_boiler (
                    bid integer primary key,
                    data text not null
                    )''')

        cur.execute('''
                    insert into last_boiler(data) values ("starting")
                    ''')

        cur.execute('''
                    create table thoughts (
                    tid integer primary key,
                    prompt text not null,
                    data text not null
                    )''')
        conn.commit()
        conn.close()

