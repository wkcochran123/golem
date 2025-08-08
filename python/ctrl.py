import sqlite3
import html
import argparse
from flask import Flask, request, send_file, make_response
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import os
from db import DB
import html

from context import ContextManager

app = Flask(__name__)
CORS(app)
INSTALLDIR = Path(os.path.join(os.environ["HOME"], "golem/python"))

def build_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset", action="store_true", help="Reset the system state to blank"
        )
    parser.add_argument(
        "--root_directory",
        default=os.getcwd(),
        help="Path to the root of the install (default: current working directory)",
        )
    return parser.parse_args()


def fix_text(text):
    return html.escape(text).replace("\n","&nbsp;<br>")

def title(text):
    return f"<font size=+2>{text}</font><br>&nbsp;</br>"

@app.route("/send", methods=["POST"])
def send():
    prompt = ContextManager.USER_PROMPT_START + request.get_json()["prompt"]

    DB.queue_prompt(prompt)
    
    return "Success"

@app.route("/dummy")
def dummy():
    return "100"

@app.route("/mood")
def mood():
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("SELECT mid,mood FROM mood ORDER BY mid desc")
    rows = cur.fetchall()
    for row in rows:
        return f"{row[1]},{row[0]}"
    return "0,-1"


    conn.close()
    return answer

@app.route("/goals")
def goals():
    result = title("Goals") + "<div style=\"width: 800px; height: 600px; overflow: auto;\"><table><tr><th>gid</th><th>Progress</th><th>Timestamp</th><th>Description</th></tr>"

    odd = True
    for row in DB.select("SELECT gid, progress, timestamp, description FROM goals ORDER BY gid"):
        tr = "<tr bgcolor=202060>" if odd else "<tr>"
        odd = not odd
        result = result + f"{tr}<td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{fix_text(row[3])}</tr>"

    result = result + f"</table>"

    return result

@app.route("/files")
def files():
    files = [f for f in Path(DB.PREFS.get("inout directory")).iterdir() if f.is_file()]

    answer = title("Files")
    for file in sorted(files):
        fname = f"{file}".split("/")[-1]
        answer = (
            answer + f"<a href=# class=\"link\" onclick=\"fetchFile('{fname}')\")>{fname}</a>&nbsp;\n"
        )

    answer = answer + f"<div style=\"left: 120;width 800px; height: 600px; overflow: auto;\" id=\"browser\"></div>"
    return answer

@app.route("/file/<fname>")
def file(fname):
    name = DB.PREFS.get("inout directory")+f"/{fname}"
    with open(name, "r") as f:
        content = f.read()
    return f"<pre>\n{content}\n</pre>"

@app.route("/robot_console")
def robot_console():
    result = "<font size=+2>Robot Console</font><br>&nbsp;<br><div style=\"width: 800px; height: 600px; overflow: auto;\"><table>"
    odd = True
    for row in DB.select("SELECT command,result,timestamp FROM robot_console"):
        td = "<td bgcolor=202060>" if odd else "<td>"
        odd = not odd
        result = result + f"<tr>{td}robot [{row[2]}]> {fix_text(row[0])}</td></tr>"
        result = result + f"<tr>{td}{fix_text(row[1])}</td></tr>"
        result = result + f"<tr>{td}&nbsp;</td></tr>"

    result = result + "</table></div>"
    return result

@app.route("/tables")
def tables():
    result = title("Tables")
    result = result + "stimuli/response:<br><table><tr><th>sid</th><th>Prompt Timestamp</th><th>Prompt</th><th>Context</th><th>Response Timestamp</th><th>Response</th><th>Thinking (if available)</th></tr>"
    for row in DB.select("select * from stimuli left outer join response on stimuli.sid = response.sid"):
        if row[7] is not None:
            result = result + f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[6]}</td><td onmouseover=callout(\"row[7]\") onmouseout=hidecallout()>{row[7][0:100]}...</td><td>{row[8][0:100]}...</td></tr>"
        else:
            result = result + f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    result = result + "</table>"
    return result


@app.route("/dialog")
def dialog():
    result = title("Robot Dialog") + "<table cellpadding=8><tr><th align=left>User</th><th align=right>Robot</th></tr>"
    for row in DB.select("SELECT stimuli.prompt, response.response from stimuli,response WHERE stimuli.sid = response.sid"):
        if row[0].startswith(ContextManager.USER_PROMPT_START):
            result = result + f"<tr><td bgcolor=202060 colspan=2 align=left>{fix_text(row[0].split(ContextManager.USER_PROMPT_START)[1])}</td></tr>"
        if row[1].strip().startswith("speak"):
            words = row[1].strip().split("speak")[1].split("|||")[0]
            result = result + f"<tr><td colspan=2 align=right>{fix_text(words)}</td></tr>"
    for row in DB.select("SELECT prompt from stimuli WHERE sid NOT IN (SELECT sid FROM response)"):
        if row[0].startswith(ContextManager.USER_PROMPT_START):
            result = result + f"<tr><td bgcolor=202060 colspan=2 align=left>{fix_text(row[0].split(ContextManager.USER_PROMPT_START)[1])}</td></tr>"
    result = result + "<tr><td colspan=2><textarea rows=2 cols=100 id=\"prompt\"></textarea><input type=button value=\"send\" onclick=\"sendPrompt()\"></table>"

    return result



@app.route("/internals")
def internals():
    result = title("Current Internal State")
    (prompt,context) = DB.pop_prompt()
    result = f"{result}Current context: {context}<br>\nCurrent prompt: {prompt}\n<br>"
    return result

@app.route("/preferences")
def preferences():
    preferences = title("Preferences") + "<table cellpadding=8><tr><th>Description:</th><th>Key:</th><th>Value:</th></tr>"

    odd = True
    for pref_row in DB.select("SELECT pid,key,value,description FROM preferences ORDER BY pid"):
        tr = "<tr bgcolor=202060>" if odd else "<tr>"
        odd = not odd
        preferences = preferences + f"{tr}<td>{html.escape(pref_row[3])}</td><td>{html.escape(pref_row[1])}</td><td>{html.escape(pref_row[2])}</td></tr>"

    result = f"{preferences}"
    return result

@app.route("/")
def home():
    main_page = '''
<html>
 <head>
 <script language="javascript">

var current_screen = "none"

async function sendPrompt() {
    const prompt = document.getElementById("prompt").value;

    try {
      const response = await fetch("/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ prompt: prompt })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.text(); // or .json()
      console.log("Server response:", result);
    } catch (error) {
      console.error("Fetch error:", error);
    }
}

function refresh() {
    if (document.getElementById("running").checked) {
        if (current_screen !== "none") 
            fetchAndDisplay(current_screen);
    }
    setTimeout(refresh,1000);
}

setTimeout(refresh, 1000);

let display_data = ""

async function fetchAndDisplay(endpoint) {
    try {
      const response = await fetch(endpoint);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.text(); // or .json() if expecting JSON
      if (display_data != data) {
          document.getElementById("display").innerHTML = data;
          display_data = data
      }
      current_screen = endpoint
    } catch (error) {
      console.error("Fetch error:", error);
      document.getElementById("display").innerHTML = `<pre style="color:red;">Error: ${error.message}</pre>`;
    }
}

async function fetchFile(fname) {
    try {
      const response = await fetch("file/"+fname);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.text(); // or .json() if expecting JSON
      document.getElementById("browser").innerHTML = data;
    } catch (error) {
      console.error("Fetch error:", error);
      document.getElementById("display").innerHTML = `<pre style="color:red;">Error: ${error.message}</pre>`;
    }
}

 </script>
 <style>
html, body {
  background-color: #101030;
  height: 100%;
  margin: 0;
  font-family: monospace;
  background-color: #101030;
  color: #ffd700;
}

a.link {
  color: #FFD700;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.2s ease;
}

a.link:hover {
  color: #FFA500; /* orange-gold on hover */
  text-decoration: underline;
}

div.menu {
  position: absolute;
  top: 20;
  left: 0;
  bottom: 0;
  right: 100px;
  overflow-y: auto; /* optional: scroll if content overflows vertically */
}

div.display {
  position: absolute;
  top: 20;
  left: 125px;
  overflow-y: auto; /* optional: scroll if content overflows vertically */
}

div.callout {
    position: absolute;
    top: 40;
    left: 40;
    right: 600;
    z-index: 10;

}

 </style>
</head>

 </head>
 <body>
  <div id="menu" class="menu">
    <table cellpadding="6">
     <tr><th bgcolor="202060"><font color="FFFFFF">Main Menu</font></th></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('dialog')">Dialog</a></td></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('goals')">Goals</a></td></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('files')">Files</a></td></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('robot_console')">Console</a></td></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('internals')">Internals</a></td></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('tables')">Tables</a></td></tr>
     <tr><td bgcolor="202060"><a href=# class="link" onclick="fetchAndDisplay('preferences')">Preferences</a></td></tr>
    </table>
    <input type="checkbox" id="running" checked>auto-update
  </div>
  <div id="display" class="display">
  </div>
  <div id="callout" class="callout">
 </body>
</html>
    '''

    return main_page

# Start up the database
args = build_argparse()
DB.stat_db(args.root_directory)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
