import sqlite3



conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
cur = conn.cursor()

cur.execute("drop table goals")
cur.execute("drop table stimuli")
cur.execute("drop table response")
cur.execute("drop table memories")
cur.execute("drop table memory_lookup")
cur.execute("drop table xpert_results")
cur.execute("drop table last_boiler")

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
            progress integer not null,
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

conn.commit()
conn.close()
