import sqlite3
import html
from flask import Flask, request, send_file
from datetime import datetime
from pathlib import Path
import os

app = Flask(__name__)
INSTALLDIR = Path(os.path.join(os.environ["HOME"], "golem/raspberrypi"))

def commit_data(sql,val):
    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute(sql,val)
    conn.commit()
    conn.close()

def cdt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/ask', methods=['POST'])
def submit():
    prompt = request.get_json()['prompt']
    commit_data("INSERT INTO stimuli (timestamp, prompt) VALUES ( ? , ? )",(cdt(),f"USER (never respond directly to USER prompts, always make a goal to accomplish the prompt.):{prompt}"))
    return "Success"

@app.route("/goals")
def goals():
    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("SELECT gid,progress,description FROM goals WHERE progress != 1")
    rows = cur.fetchall()
    answer = "<table valign=top><tr><th>gid</th><th>progress</th><th>description</th></tr>"
    for row in rows:
        answer += f"<tr valign=top><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    answer = answer + "</table>"
    conn.close()
    return answer

@app.route("/files")
def files():
    files = [f for f in Path( INSTALLDIR / "inout").iterdir() if f.is_file()]

    answer = ""
    for file in sorted(files, reverse=True):
        fname = f"{file}".split("/")[-1]
        answer = answer + f"<a href=# onclick=\"fetchFile('{fname}')\")>{fname}</a>&nbsp;\n"

    return answer

@app.route("/dummy")
def dummy():
    return "100"

@app.route("/picslist")
def picslist():
    files = [f for f in Path( INSTALLDIR / "pics").iterdir() if f.is_file()]

    answer = ""
    for file in sorted(files, reverse=True):
        fname = f"{file}".split("/")[-1]
        answer = answer + f"<a href=# onclick=\"fetchPic('{fname}')\")>{fname}</a><br>\n"
    return answer

@app.route("/backlog")
def backlog():
    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("select prompt from stimuli where sid not in (select sid from response)")
    rows = cur.fetchall()
    answer = "<table valign=top>"
    for row in rows:
        answer += f"<tr valign=top><td><pre>{row[0]}</pre></td></tr>"
    answer = answer + "</table>"
    conn.close()
    return answer

@app.route("/boiler")
def boiler():
    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("SELECT data FROM last_boiler")
    rows = cur.fetchall()
    for row in rows:
        return f"<pre>\n{row[0]}\n</pre>"
    return ""

@app.route("/pic/<fname>")
def pic(fname):
    return send_file (INSTALLDIR / f"pics/{fname}", mimetype='image/jpeg')

@app.route("/file/<fname>")
def file(fname):
    return send_file (INSTALLDIR / f"inout/{fname}", mimetype='image/jpeg')

@app.route("/printable/<thoughtful>")
def printable(thoughtful):
    print (f"{thoughtful}")
    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()
    cur.execute("SELECT stimuli.prompt, response.think, response.response FROM stimuli,response WHERE stimuli.sid = response.sid order by stimuli.sid asc")
    rows = cur.fetchall()
    answer = "";
    for row in rows:
        r0 = html.escape(row[0]).replace("\n","<br>")
        r1 = html.escape(row[1]).replace("\n","<br>")
        r2 = html.escape(row[2]).replace("\n","<br>")
        llm = ""
        if thoughtful == "true":
            llm = f"<br><b>llm thoughts:</b><br><i>{r1}</i>"
        answer += f"<b>prompt:</b><br>{r0}{llm}<br><b>command:</b><br><pre>{r2}<pre><br>&nbsp;<br>"
    conn.close()
    return answer
@app.route("/dialog")
def dialog():
    conn = sqlite3.connect("dommy.sqlite", timeout=5.0)
    cur = conn.cursor()

    cur.execute("SELECT stimuli.prompt, response.think, response.response FROM stimuli,response WHERE stimuli.sid = response.sid order by stimuli.sid desc")
    rows = cur.fetchall()
    answer = "<table><tr><th width=33%>prompt</th><th width=33%>think</th><th width=33%>response</th></tr>"
    for row in rows:
        answer += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td></tr>"
    answer = answer + "</table>"
    conn.close()
    return answer


@app.route("/")
def home():
    base_url = request.host_url
    main_page = f'''
    <html><head>
    <script language=javascript>
        function getEndPoint(ep) {{
            website="http://127.0.0.1:8000/";
            return website + ep;
        }}
        function fetchBoiler() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("boiler"))
              .then(response => response.text())
              .then(data => {{
                document.getElementById("boiler").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("boiler").innerText = "Error: " + error;
              }});
       }}
        function fetchDialog() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("dialog"))
              .then(response => response.text())
              .then(data => {{
                document.getElementById("dialog").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("dialog").innerText = "Error: " + error;
              }});
       }}
        function fetchPrintable() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("printable")+"/"+document.getElementById("thoughtful").checked)
              .then(response => response.text())
              .then(data => {{
                document.getElementById("printable").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("printable").innerHTML = "Error: " + error;
              }});
       }}
        function fetchBacklog() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("backlog"))
              .then(response => response.text())
              .then(data => {{
                document.getElementById("backlog").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("backlog").innerHTML = "Error: " + error;
              }});
       }}
        function fetchFiles() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("files"))
              .then(response => response.text())
              .then(data => {{
                document.getElementById("files").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("files").innerText = "Error: " + error;
              }});
       }}
        function fetchGoals() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("goals"))
              .then(response => response.text())
              .then(data => {{
                document.getElementById("goals").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("goals").innerText = "Error: " + error;
              }});
       }}
        function fetchPicsList() {{
            if (!document.getElementById("running").checked) return;
            fetch(getEndPoint("picslist"))
              .then(response => response.text())
              .then(data => {{
                document.getElementById("picslist").innerHTML = data;
              }})
              .catch(error => {{
                document.getElementById("picslist").innerText = "Error: " + error;
              }});
       }}
        function fetchPic(pic) {{
            document.getElementById("pic").src=getEndPoint("pic") +"/"+pic;
       }}
        function fetchFile(file) {{
            document.getElementById("filescreen").innerHTML=getEndPoint("file") +"/"+file;
            fetch(getEndPoint("file") + "/" + file)
              .then(response => response.text())
              .then(data => {{
                document.getElementById("filescreen").innerHTML = "<pre>" + data + "</pre>";
              }})
              .catch(error => {{
                document.getElementById("filescreen").innerText = "Error: " + error;
              }});
       }}
         function sendText() {{
                const prompt = document.getElementById("promptInput").value;
                document.getElementById("lastq").innerHTML = prompt;
                fetch(getEndPoint("ask"), {{
                  method: "POST",
                  headers: {{"Content-Type": "application/json"}},
                  body: JSON.stringify({{ prompt: prompt }})
                }})
                .then(res => res.text())
                .then(data => {{
                  document.getElementById("response").innerHTML = data;
                }});
              }}

       current_show = null;
       function show(screen) {{
            if (current_show != null) {{
                current_show.style.display = 'none';
            }}
            current_show = document.getElementById(screen);
            current_show.style.display = 'block';
       }}



       function go() {{
            setInterval(fetchGoals,1000);
            setInterval(fetchDialog,1000);
            setInterval(fetchPrintable,1000);
            setInterval(fetchPicsList,1000);
            setInterval(fetchBoiler,1000);
            setInterval(fetchBacklog,1000);
            setInterval(fetchFiles,1000);
            document.getElementById("inner").style.display = 'none';
            document.getElementById("images").style.display = 'none';
            document.getElementById("mind").style.display = 'none';
            document.getElementById("printable").style.display = 'none';
            document.getElementById("backlog").style.display = 'none';
            document.getElementById("files").style.display = 'none';
            
       }}
    </script>
    </head>
    <body onload="go()">
    <div id="top">
    <input type="text" size=200 id="promptInput">
    <button onclick="sendText()">Send</button>
    <br>
    <div id="lastq"></div><br>
    <table> <tr>
    <td><a href=# onclick="show('inner')">Inner dialog</a></td>
    <td><a href=# onclick="show('images')">Images</a></td>
    <td><a href=# onclick="show('mind')">Context</a></td>
    <td><a href=# onclick="show('printable')">Printable</a><input type=checkbox id="thoughtful">thoughtful</td>
    <td><a href=# onclick="show('backlog')">Backlog</a></td>
    <td><a href=# onclick="show('files')">Files</a></td>
    <td><input type=checkbox id="running" checked>running</td>
    </tr> </table>
    </div>


    <div id="inner">
    <table><tr><td width=70% id="dialog"></td><td valign=top width=30% id="goals"></td></tr></table>
    </div>

    <div id="backlog">
    </div>

    <div id="printable">
    </div>

    <div id="files">
    </div>

    <div id="mind">
    <table><tr><td width=100% id="boiler"></td></tr></table>
    </div>

    <div id="filescreen">
    </div>

    
    <div id="images">
    <table><tr><td width=20% id="picslist"></td><td><img src="http:127.0.0.1/asdf.jpg" id="pic"></td></table>
    </div>


    </body>
    </html>'''
    
    return main_page

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
