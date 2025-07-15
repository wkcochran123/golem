import sqlite3
import os
from datetime import datetime

class DB:
    """
        DB helper class
    """
    DB_PATH = None
    PREFS = None

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
    def single_value(query,values=()):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute(query,values)
        rows = cur.fetchall()
        for row in rows:
            conn.commit()
            conn.close()
            return row[0]
        conn.commit()
        conn.close()
        return None

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
    def queue_prompt(prompt,context="robot"):
        DB.commit("INSERT INTO stimuli (timestamp,prompt,context) VALUES(?,?,?)",(DB.cdt(),prompt,context))

    @staticmethod
    def pop_prompt():
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute("select prompt,context from stimuli where sid not in (select sid from response)")
        rows = cur.fetchall()
        prompt = None
        context = None
        for row in rows:
            prompt = row[0]
            context = row[1]
            break
        conn.commit()
        conn.close()
        return (prompt,context)

    @staticmethod
    def reset ():
        os.remove(DB.DB_PATH)
        DB.stat_db(None)

    @staticmethod
    def stat_db (sqlite_bootstrap):
        if sqlite_bootstrap == None:
            sqlite_bootstrap = input (f"Please put in the path to your SQLite DB [enter for current PWD: {os.getcwd()}]")
        if sqlite_bootstrap == "":
            sqlite_bootstrap = os.getcwd();

        DB.DB_PATH = sqlite_bootstrap + "/core.sqlite";
        try:
            os.stat(DB.DB_PATH)
        except Exception as e:
            print (f"No database found, building.")
            DB.build_database(sqlite_bootstrap)

        DB.PREFS = Prefs()

    @staticmethod
    def build_database(path):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS goals")
        cur.execute("DROP TABLE IF EXISTS stimuli")
        cur.execute("DROP TABLE IF EXISTS response")
        cur.execute("DROP TABLE IF EXISTS memories")
        cur.execute("DROP TABLE IF EXISTS memory_lookup")
        cur.execute("DROP TABLE IF EXISTS robot_console")
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
                    prompt text not null,
                    context text not null
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
                    test_script text not null,
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
                    create table robot_console (
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
        cur.execute("insert into preferences (key,value) values(?,?)",("context types","robot,coder"))
        cur.execute("insert into preferences (key,value) values(?,?)",("robot generators","robot_instructions,robot_console"))
        cur.execute("insert into preferences (key,value) values(?,?)",("coder generators","robot_console"))

        conn.commit()
        conn.close()


class Prefs:
    """
        Prefs class used to configure everything.  Use this to store magic numbers,
        meta parameters, etc.
    """
    def __init__ (self):
        self.reload()

    def reload(self):
        self._preferences = dict()
        for row in DB.select("select key, value from preferences", ()):
            self._preferences[row[0]] = row[1]
        
    def get (self,pref,default=None):
        if pref not in self._preferences:
            value = default if default is not None else input (f"Unknown preference '{pref}' and no default value was provided. Please input a value: ")
            self.set(pref,value)
        return self._preferences[pref]

    def set (self,pref,value):
        DB.commit ("DELETE FROM preferences WHERE key = ?",(pref,))
        DB.commit ("INSERT INTO preferences (key,value) VALUES ( ? , ?)", (pref,value))
        self._preferences[pref] = value
