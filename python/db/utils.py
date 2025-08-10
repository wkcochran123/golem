import sqlite3
import os
from datetime import datetime


class DB:
    """
    DB helper class
    """

    DB_PATH = None
    PREFS = None
    INOUT_DIRECTORY = "inout directory"

    def __init__(self):
        pass

    @staticmethod
    def cdt():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def commit(query, values=()):
        try:
            conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
            cur = conn.cursor()
            cur.execute(query, values)
        except sqlite3.Error as e:
            print(f"val: {values}")
            print(f"SQLite3 execute error: {e}")
        conn.commit()
        conn.close()

    @staticmethod
    def single_value(query, values=()):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute(query, values)
        rows = cur.fetchall()
        for row in rows:
            conn.commit()
            conn.close()
            return row[0]
        conn.commit()
        conn.close()
        return None

    @staticmethod
    def select(query, values=()):
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute(query, values)
        rows = cur.fetchall()
        for row in rows:
            yield row
        conn.commit()
        conn.close()

    @staticmethod
    def big_strip(text):
        return ''.join([c for i, c in enumerate(s) if c not in " \t\n\"'"] or [s[0]])

    @staticmethod
    def queue_prompt(prompt, context="robot"):
        DB.commit(
            "INSERT INTO stimuli (timestamp,prompt,context) VALUES(?,?,?)",
            (DB.cdt(), prompt, context),
        )

    @staticmethod
    def add_console_line(command, result, timestamp):
        DB.commit(
            "INSERT INTO robot_console (command,result,timestamp) VALUES (?,?,?)",
            (command, result, DB.cdt()),
        )

    @staticmethod
    def add_prompt_response(prompt, response, context, prompt_timestamp):
        sides = response.split("</think>")
        think = ""
        if len(sides) > 1:
            response = sides[-1]
            think = sides[0]
        sid = DB.single_value(
            "select sid from stimuli where sid not in (select sid from response)"
        )
        if sid is None:
            conn = sqlite3.connect(DB.DB_PATH, timeout=10.0)
            cursor = conn.cursor()
            try:
                cursor.execute("BEGIN")  # start transaction
                cursor.execute(
                    "INSERT INTO stimuli (prompt,context,timestamp)  VALUES (?,?,?)",
                    (prompt, context, prompt_timestamp),
                )
                sid = cursor.lastrowid  # get the primary key
                cursor.execute(
                    "INSERT INTO response (sid,response,think,timestamp) VALUES (?,?,?,?)",
                    (sid, response, think, DB.cdt()),
                )
            except Exception as e:
                print(f"Execute exception: {e}")
                raise Exception(e)

            conn.commit()
            conn.close()
            return
        DB.commit(
            "INSERT INTO response (sid,response,think,timestamp) VALUES (?,?,?,?)",
            (sid, response, think, DB.cdt()),
        )

    @staticmethod
    def pop_prompt():
        conn = sqlite3.connect(DB.DB_PATH, timeout=5.0)
        cur = conn.cursor()
        cur.execute(
            "select prompt,context from stimuli where sid not in (select sid from response) order by sid asc"
        )
        rows = cur.fetchall()
        prompt = None
        context = None
        for row in rows:
            prompt = row[0]
            context = row[1]
            break
        conn.commit()
        conn.close()
        return (prompt, context)

    URL = None

    @staticmethod
    def reset():
        DB.URL = DB.PREFS.get(
            "chat/completion url",
            description="This is the url that expects the v1/chat/completions endpoint to exist. http[s]://<ip address>:<port>",
        )
        os.remove(DB.DB_PATH)
        DB.stat_db(None)

    @staticmethod
    def stat_db(sqlite_bootstrap):
        if sqlite_bootstrap == None:
            sqlite_bootstrap = input(
                f"Please put in the path to your SQLite DB [enter for current PWD: {os.getcwd()}]"
            )
        if sqlite_bootstrap == "":
            sqlite_bootstrap = os.getcwd()

        DB.DB_PATH = sqlite_bootstrap + "/core.sqlite"
        try:
            os.stat(DB.DB_PATH)
        except Exception as e:
            print(f"No database found, building.")
            DB.build_database(sqlite_bootstrap)

        DB.PREFS = Prefs()
        if DB.URL:
            DB.PREFS.set(
                "chat/completion url",
                DB.URL,
                description="This is the url that expects the v1/chat/completions endpoint to exist. http[s]://<ip address>:<port>",
            )
        DB.URL = None

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
        cur.execute("DROP TABLE IF EXISTS prompts")
        cur.execute(
            """
                    create table preferences (
                    pid integer primary key,
                    key text not null,
                    value text not null,
                    description not null
                    )"""
        )
        cur.execute(
            """
                    create table stimuli (
                    sid integer primary key,
                    timestamp text not null,
                    prompt text not null,
                    context text not null
                    )"""
        )

        cur.execute(
            """
                    create table response (
                    rid integer primary key,
                    sid integer unique,
                    timestamp text not null,
                    response text not null,
                    think text not null
                    )"""
        )

        cur.execute(
            """
                    create table goals (
                    gid integer primary key,
                    progress float not null,
                    timestamp text not null,
                    description text not null
                    )"""
        )

        cur.execute(
            """
                    create table memories (
                    mid integer primary key,
                    description text not null,
                    timestamp text not null
                    )"""
        )

        cur.execute(
            """
                    create table memory_lookup (
                    mid integer not null,
                    sid integer not null
                    )"""
        )

        cur.execute(
            """
                    create table robot_console (
                    xid integer primary key,
                    command text not null,
                    result text not null,
                    timestamp text not null
                    )"""
        )

        cur.execute(
            """
                    create table last_boiler (
                    bid integer primary key,
                    data text not null
                    )"""
        )

        cur.execute(
            """
                    insert into last_boiler(data) values ("starting")
                    """
        )

        cur.execute(
            """
                    create table thoughts (
                    tid integer primary key,
                    prompt text not null,
                    data text not null
                    )"""
        )
        cur.execute(
            """
                    create table mood (
                    mid integer primary key,
                    mood integer not null
                    )"""
        )
        cur.execute(
            """
                    create table prompts (
                    pid integer primary key,
                    level integer,
                    timestamp text not null,
                    prompt text
                    )"""
        )
        conn.commit()
        conn.close()


class Prefs:
    """
    Prefs class used to configure everything.  Use this to store magic numbers,
    meta parameters, etc.
    """

    def __init__(self):
        self.reload()

    def reload(self):
        self._preferences = dict()
        for row in DB.select("select key, value from preferences", ()):
            self._preferences[row[0]] = row[1]

    def get(self, pref, default=None, description="Description needed"):
        if pref not in self._preferences:
            value = (
                default
                if default is not None
                else input(
                    f"Unknown preference '{pref}' with descrption '{description}'. Please input a value: "
                )
            )
            self.set(pref, value, description=description)
        return self._preferences[pref]

    def describe(self, pref, description):
        self.set(pref, self.get(pref), description=description)

    def set(self, pref, value, description="Description needed"):
        DB.commit("DELETE FROM preferences WHERE key = ?", (pref,))
        DB.commit(
            "INSERT INTO preferences (key,value,description) VALUES ( ? , ? , ? )",
            (pref, value, description),
        )
        if pref.startswith("chat"):
            if description.startswith("Des"):
                print("asdf")
        self._preferences[pref] = value

    def drop(self, pref=None):
        if pref not in self._preferences:
            raise KeyError(pref)
        else:
            DB.commit("DELETE FROM preferences WHERE key = ?", (pref,))
            del self._preferences[pref]
