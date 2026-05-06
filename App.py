from flask import (
    Flask, request, jsonify, session,
    render_template, redirect, url_for
)
from Database import (
    init_db, create_user, verify_user,
    create_session, get_sessions, delete_session,
    update_session_title, add_message, get_messages,
    session_belongs_to
)
from groq import Groq
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-xyz123")

# ── Groq client (llama3-8b-8192 — free, fast, open-source) ──────────────────
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

MODEL   = "llama-3.1-8b-instant"   # lightweight open-source model via Groq
SYSTEM  = (
    "You are a helpful, concise AI assistant. "
    "Answer clearly and in the same language the user writes in."
)

init_db()   # create tables on startup

# ── Helpers ──────────────────────────────────────────────────────────────────
def logged_in():
    return "user_id" in session

def require_login():
    if not logged_in():
        return redirect(url_for("login_page"))

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if logged_in():
        return redirect(url_for("chat_page"))
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET"])
def login_page():
    if logged_in():
        return redirect(url_for("chat_page"))
    return render_template("index.html")

@app.route("/api/signup", methods=["POST"])
def signup():
    data     = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return jsonify({"ok": False, "error": "Username and password required."}), 400
    if len(password) < 4:
        return jsonify({"ok": False, "error": "Password must be ≥ 4 characters."}), 400
    ok, msg = create_user(username, password)
    if not ok:
        return jsonify({"ok": False, "error": msg}), 409
    uid = verify_user(username, password)
    session["user_id"]  = uid
    session["username"] = username
    return jsonify({"ok": True})

@app.route("/api/login", methods=["POST"])
def login():
    data     = request.get_json()
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    uid = verify_user(username, password)
    if not uid:
        return jsonify({"ok": False, "error": "Incorrect username or password."}), 401
    session["user_id"]  = uid
    session["username"] = username
    return jsonify({"ok": True})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

# ── Chat page ─────────────────────────────────────────────────────────────────
@app.route("/chat")
def chat_page():
    redir = require_login()
    if redir:
        return redir
    return render_template("index.html", username=session["username"])

# ── Session API ───────────────────────────────────────────────────────────────
@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    if not logged_in():
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True, "sessions": get_sessions(session["user_id"])})

@app.route("/api/sessions", methods=["POST"])
def new_session():
    if not logged_in():
        return jsonify({"ok": False}), 401
    sid = create_session(session["user_id"])
    return jsonify({"ok": True, "session_id": sid})

@app.route("/api/sessions/<int:sid>", methods=["DELETE"])
def del_session(sid):
    if not logged_in():
        return jsonify({"ok": False}), 401
    delete_session(sid, session["user_id"])
    return jsonify({"ok": True})

# ── Message API ───────────────────────────────────────────────────────────────
@app.route("/api/sessions/<int:sid>/messages", methods=["GET"])
def list_messages(sid):
    if not logged_in():
        return jsonify({"ok": False}), 401
    if not session_belongs_to(sid, session["user_id"]):
        return jsonify({"ok": False}), 403
    return jsonify({"ok": True, "messages": get_messages(sid)})

@app.route("/api/sessions/<int:sid>/chat", methods=["POST"])
def chat(sid):
    if not logged_in():
        return jsonify({"ok": False}), 401
    if not session_belongs_to(sid, session["user_id"]):
        return jsonify({"ok": False}), 403

    data    = request.get_json()
    user_q  = (data.get("message") or "").strip()
    if not user_q:
        return jsonify({"ok": False, "error": "Empty message."}), 400

    # Save user turn
    add_message(sid, "user", user_q)

    # Update session title from first user message
    history = get_messages(sid)
    if len(history) == 1:
        update_session_title(sid, user_q[:60])

    # Build message list for Groq (role + content only)
    groq_msgs = [{"role": m["role"], "content": m["content"]} for m in history]

    # Call Groq → llama3-8b (open-source, lightweight)
    try:
        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": SYSTEM}] + groq_msgs,
            max_tokens=1024,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"[Model error: {e}]"

    # Save assistant turn
    add_message(sid, "assistant", reply)

    return jsonify({"ok": True, "reply": reply})

# ── Whoami ─────────────────────────────────────────────────────────────────────
@app.route("/api/whoami")
def whoami():
    if not logged_in():
        return jsonify({"loggedIn": False})
    return jsonify({"loggedIn": True, "username": session["username"]})

if __name__ == "__main__":
    app.run(debug=True, port=5000)