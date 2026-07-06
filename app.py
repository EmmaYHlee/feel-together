import os, uuid, random, base64, hashlib, sqlite3
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, make_response, jsonify, send_from_directory,
)
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = "s3cr3t_k3y_f0r_fl4sk_s3ss10n"

# ── Config ──────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(__file__)
DB_PATH    = os.path.join(BASE_DIR, "feeltogether.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
VALID_MOODS = {"happy", "sad", "angry", "boring"}
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Music ────────────────────────────────────────────────────
SONGS = {
    "happy":  [{"title": "Happy Vibes",  "file": "music/happy.mp3"}],
    "sad":    [{"title": "Rainy Days",   "file": "music/sad.mp3"}],
    "angry":  [{"title": "Fire Fury",  "file": "music/angry.mp3"}],
    "boring": [{"title": "Drift Away",   "file": "music/boring.mp3"}],
}

def pick_song(mood):
    if not mood or mood not in SONGS:
        return None
    return random.choice(SONGS[mood])

# ── Database ─────────────────────────────────────────────────
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    return db

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL UNIQUE COLLATE NOCASE,
            email      TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password   TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS doodles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
            emotion     TEXT NOT NULL,
            image_url   TEXT NOT NULL,
            description TEXT NOT NULL,
            likes       INTEGER DEFAULT 0,
            dislikes    INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS reactions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            doodle_id INTEGER NOT NULL REFERENCES doodles(id) ON DELETE CASCADE,
            type      TEXT NOT NULL,
            UNIQUE(user_id, doodle_id)
        );
    """)
    db.commit()
    db.close()

# ── Helpers ──────────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def get_mood():
    mood = request.cookies.get("mood", "").lower()
    return mood if mood in VALID_MOODS else None

def current_user():
    """Return dict with id/username from session, or None."""
    if "user_id" in session:
        return {"id": session["user_id"], "username": session["username"]}
    return None

def save_dataurl(data_url):
    _, b64 = data_url.split(",", 1)
    img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGBA")
    bg  = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    if bg.width > 1200:
        r  = 1200 / bg.width
        bg = bg.resize((1200, int(bg.height * r)), Image.LANCZOS)
    name = f"{uuid.uuid4().hex}.png"
    bg.save(os.path.join(UPLOAD_DIR, name), "PNG", optimize=True)
    return f"/uploads/{name}"

# ════════════════════════════════════════════════════════════
#  PAGE ROUTES
# ════════════════════════════════════════════════════════════

@app.route("/")
def home():
    resp = make_response(render_template("home.html", page="home",
                                         mood=None, user=current_user()))
    resp.delete_cookie("mood")
    return resp


@app.route("/set_mood/<mood>")
def set_mood(mood):
    mood = mood.lower()
    if mood not in VALID_MOODS:
        return redirect(url_for("home"))
    dest = url_for("board") if request.args.get("next") == "board" else url_for("draw")
    resp = make_response(redirect(dest))
    resp.set_cookie("mood", mood, max_age=60 * 60 * 24 * 7)
    return resp


@app.route("/draw")
def draw():
    mood = get_mood()
    song = pick_song(mood)
    return render_template("draw.html", page="draw", mood=mood,
                           song_file=song["file"] if song else None,
                           song_title=song["title"] if song else None,
                           user=current_user())


@app.route("/board")
def board():
    mood = get_mood()
    song = pick_song(mood)
    return render_template("board.html", page="board", mood=mood,
                           song_file=song["file"] if song else None,
                           song_title=song["title"] if song else None,
                           user=current_user())


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        mode = request.args.get("mode", "signup")
        mood = get_mood()
        song = pick_song(mood)
        return render_template("signup.html", page="signup",
                               mood=mood, user=current_user(), error=None, mode=mode,
                               song_file=song["file"] if song else None,
                               song_title=song["title"] if song else None)

    # ── Handle form POST ──
    mode = request.form.get("mode", "signup")
    mood = get_mood()
    song = pick_song(mood)
    def _signup_page(error, m=None):
        return render_template("signup.html", page="signup", mood=mood,
                               user=None, error=error, mode=m or mode,
                               song_file=song["file"] if song else None,
                               song_title=song["title"] if song else None)

    if mode == "login":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        db.close()
        if not user or user["password"] != hash_pw(password):
            return _signup_page("Wrong username or password.", "login")
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("home"))

    # mode == signup
    username = request.form.get("username", "").strip()
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm  = request.form.get("confirm", "")

    if len(username) < 3:
        return _signup_page("Username must be at least 3 characters.")
    if "@" not in email:
        return _signup_page("Enter a valid email.")
    if len(password) < 6:
        return _signup_page("Password must be at least 6 characters.")
    if password != confirm:
        return _signup_page("Passwords do not match.")

    db = get_db()
    try:
        cur = db.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)",
                         (username, email, hash_pw(password)))
        db.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        db.close()
        return _signup_page("Username or email already taken.")
    db.close()

    session["user_id"]  = user_id
    session["username"] = username
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/clear_mood")
def clear_mood():
    resp = make_response(redirect(url_for("home")))
    resp.delete_cookie("mood")
    return resp


@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ════════════════════════════════════════════════════════════
#  API — DOODLES  (used by JS fetch in draw/board pages)
# ════════════════════════════════════════════════════════════

@app.route("/api/doodles", methods=["POST"])
def api_create_doodle():
    data        = request.get_json(force=True)
    emotion     = (data.get("emotion") or "").strip()
    description = (data.get("description") or "").strip()
    image_data  = data.get("imageData", "")

    if emotion not in VALID_MOODS:
        return jsonify({"error": "Invalid emotion"}), 400
    if not description:
        return jsonify({"error": "Description required"}), 400
    if not image_data.startswith("data:"):
        return jsonify({"error": "Invalid image"}), 400

    try:
        image_url = save_dataurl(image_data)
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

    user_id = session.get("user_id")  # None if not logged in — stored as NULL
    db  = get_db()
    cur = db.execute(
        "INSERT INTO doodles (user_id, emotion, image_url, description) VALUES (?,?,?,?)",
        (user_id, emotion, image_url, description)
    )
    db.commit()
    doodle_id = cur.lastrowid
    row = dict(db.execute("SELECT * FROM doodles WHERE id=?", (doodle_id,)).fetchone())
    db.close()

    row["user_reaction"] = None
    row["username"]      = session.get("username")
    row["image_url"]     = request.host_url.rstrip("/") + row["image_url"]
    return jsonify(row), 201


@app.route("/api/doodles", methods=["GET"])
def api_list_doodles():
    emotion = request.args.get("emotion", "").strip()
    user_id = session.get("user_id")

    db = get_db()
    if user_id:
        sql  = """SELECT d.*, u.username, r.type AS user_reaction
                  FROM doodles d
                  LEFT JOIN users u ON u.id = d.user_id
                  LEFT JOIN reactions r ON r.doodle_id=d.id AND r.user_id=?
                  {} ORDER BY d.created_at DESC""".format(
                      "WHERE d.emotion=?" if emotion else "")
        args = [user_id, emotion] if emotion else [user_id]
    else:
        sql  = """SELECT d.*, u.username, NULL AS user_reaction
                  FROM doodles d LEFT JOIN users u ON u.id=d.user_id
                  {} ORDER BY d.created_at DESC""".format(
                      "WHERE d.emotion=?" if emotion else "")
        args = [emotion] if emotion else []

    rows = db.execute(sql, args).fetchall()
    db.close()

    host   = request.host_url.rstrip("/")
    result = []
    for row in rows:
        r = dict(row)
        if r["image_url"] and not r["image_url"].startswith("http"):
            r["image_url"] = host + r["image_url"]
        result.append(r)
    return jsonify(result), 200


@app.route("/api/doodles/<int:doodle_id>", methods=["DELETE"])
def api_delete_doodle(doodle_id):
    if not current_user():
        return jsonify({"error": "Login required"}), 401

    db  = get_db()
    row = db.execute("SELECT user_id FROM doodles WHERE id=?", (doodle_id,)).fetchone()
    if not row:
        db.close()
        return jsonify({"error": "Doodle not found"}), 404
    if row["user_id"] != session["user_id"]:
        db.close()
        return jsonify({"error": "You can only delete your own doodles"}), 403

    db.execute("DELETE FROM doodles WHERE id=?", (doodle_id,))
    db.commit()
    db.close()
    return jsonify({"ok": True}), 200

@app.route("/api/doodles/<int:doodle_id>/react", methods=["POST"])
def api_react(doodle_id):
    if not current_user():
        return jsonify({"error": "Login required"}), 401

    rtype = (request.get_json(force=True).get("type") or "").strip()
    if rtype not in ("like", "dislike"):
        return jsonify({"error": "Invalid type"}), 400

    db = get_db()

    if not db.execute("SELECT 1 FROM doodles WHERE id=?", (doodle_id,)).fetchone():
        db.close()
        return jsonify({"error": "Not found"}), 404

    col = "likes" if rtype == "like" else "dislikes"
    db.execute(f"UPDATE doodles SET {col}={col}+1 WHERE id=?", (doodle_id,))
    db.commit()

    row = db.execute("SELECT likes,dislikes FROM doodles WHERE id=?", (doodle_id,)).fetchone()
    db.close()
    return jsonify({"likes": row["likes"], "dislikes": row["dislikes"], "user_reaction": rtype}), 200

if __name__ == "__main__":
    init_db()
    print("DB ready — http://localhost:5000")
    app.run(debug=True, port=5000)
