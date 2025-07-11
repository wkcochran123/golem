import subprocess
import sqlite3

def test_triple_value (command_line, sql_statement, value):
    cmd = ['python','brain.py']+command_line
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=False, timeout=300)
    except Exception as e:
        subprocess.run(['rm', '-f', 'dommy.sqlite'])
        return f"ERROR: {e}"

    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute(sql_statement)
    rows = cur.fetchall()
    answer = None
    for row in rows:
        answer = row[0]
        break;
    if str(value) != str(answer):
        return f"ERROR: Expected {value}, found {answer}"

    subprocess.run(['rm', '-f', 'dommy.sqlite'])
    return "Passed"


tests = [
    ("hello_world", ["noop"], "select 1", "1")
    ]

for (name,command_line,sql_statement,value) in tests:
    result = test_triple_value (command_line,sql_statement,value)
    print (f"TEST {name}:\n{result}")
