from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from pathlib import Path
import os
import sqlite3

app = Flask(__name__)
CORS(app)
INSTALLDIR = Path(os.path.join(os.environ["HOME"], "golem/python"))

def commit_data(sql, val):
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    cur = conn.cursor()
    cur.execute(sql, val)
    conn.commit()
    conn.close()

def cdt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route("/api/prompt", methods=["POST"])
def submit_prompt():
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Prompt is required"}), 400
    
    prompt = data["prompt"]
    commit_data(
        "INSERT INTO stimuli (timestamp, prompt) VALUES ( ? , ? )",
        (cdt(), f"USER:{prompt}"),
    )
    return jsonify({"status": "success", "message": "Prompt submitted"})

@app.route("/api/goals")
def get_goals():
    limit = request.args.get('limit', default=10, type=int)
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT gid, progress, description 
        FROM goals 
        WHERE progress != 1 
        ORDER BY gid DESC 
        LIMIT ?
    """, (limit,))
    goals = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"goals": goals})

@app.route("/api/files")
def get_files():
    try:
        files = [f.name for f in Path(INSTALLDIR / "inout").iterdir() if f.is_file()]
        return jsonify({"files": sorted(files, reverse=True)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/mood")
def get_mood():
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    cur = conn.cursor()
    cur.execute("SELECT mid, mood FROM mood ORDER BY mid DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return jsonify({"mood": row[1], "mid": row[0]})
    return jsonify({"mood": 0, "mid": -1})

@app.route("/api/images")
def get_images():
    try:
        files = [f.name for f in Path(INSTALLDIR / "pics").iterdir() if f.is_file()]
        return jsonify({"images": sorted(files, reverse=True)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/backlog")
def get_backlog():
    limit = request.args.get('limit', default=10, type=int)
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT sid, timestamp, prompt 
        FROM stimuli 
        WHERE sid NOT IN (SELECT sid FROM response)
        ORDER BY sid DESC 
        LIMIT ?
    """, (limit,))
    backlog = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"backlog": backlog})

@app.route("/api/context")
def get_context():
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    cur = conn.cursor()
    cur.execute("SELECT data FROM last_boiler LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return jsonify({"context": row[0] if row else ""})

@app.route("/api/dialog")
def get_dialog():
    limit = request.args.get('limit', default=10, type=int)
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT stimuli.sid, stimuli.timestamp, stimuli.prompt, 
               response.think, response.response 
        FROM stimuli, response 
        WHERE stimuli.sid = response.sid 
        ORDER BY stimuli.sid DESC 
        LIMIT ?
    """, (limit,))
    dialog = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"dialog": dialog})

@app.route("/api/printable")
def get_printable():
    limit = request.args.get('limit', default=10, type=int)
    thoughtful = request.args.get('thoughtful', default=False, type=lambda v: v.lower() == 'true')
    
    conn = sqlite3.connect("core.sqlite", timeout=5.0)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT stimuli.sid, stimuli.timestamp, stimuli.prompt, 
               response.think, response.response 
        FROM stimuli, response 
        WHERE stimuli.sid = response.sid 
        ORDER BY stimuli.sid DESC 
        LIMIT ?
    """, (limit,))
    
    printable = []
    for row in cur.fetchall():
        item = {
            "id": row["sid"],
            "timestamp": row["timestamp"],
            "prompt": row["prompt"],
            "command": row["response"]
        }
        if thoughtful:
            item["llm_thoughts"] = row["think"]
        printable.append(item)
    
    conn.close()
    return jsonify({"printable": printable})

@app.route("/api/file/<fname>")
def get_file(fname):
    try:
        file_path = INSTALLDIR / "inout" / fname
        if not file_path.is_file():
            return jsonify({"error": "File not found"}), 404
        with open(file_path, "r") as f:
            return jsonify({
                "filename": fname,
                "content": f.read()
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/image/<fname>")
def get_image(fname):
    try:
        image_path = INSTALLDIR / "pics" / fname
        if not image_path.is_file():
            return jsonify({"error": "Image not found"}), 404
        return send_file(image_path, mimetype="image/jpeg")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
