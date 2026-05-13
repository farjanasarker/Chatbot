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
# ── Commented out Groq API ──────────────────
# from groq import Groq
# import os

# ── Local LLM imports ───────────────────────
# Note: transformers is imported lazily in load_model() to avoid hanging
import torch
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-xyz123")

# ── Commented out Groq client ───────────────
# groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# ── Local LLM setup (Qwen 2.5 7B - full model for production) 1.5B , 3B ──────────
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        # Lazy import to avoid hanging on transformers initialization
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        print("[MODEL] Loading Qwen 2.5 1.5B model...")
        print("[MODEL] Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        print("[MODEL] Tokenizer loaded.")
        
        # Use device_map only if CUDA is available (GPU)
        # For CPU, load directly without device_map
        if torch.cuda.is_available():
            print("[MODEL] GPU detected. Using device_map='auto'...")
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
        else:
            print("[MODEL] CPU mode. Loading model to CPU (float32)...")
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float32,
                trust_remote_code=True
            ).to("cpu")
        
        print("[MODEL] Model loaded successfully!")

# Don't load model on startup - load on first request
# load_model()

# ── Load system prompt from file ──────────────────
def load_system_prompt():
    try:
        # Try optimized version first, fallback to original
        try:
            with open("System_Prompt_Optimized.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            with open("System_Prompt.txt", "r", encoding="utf-8") as f:
                return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful AI assistant."

SYSTEM = load_system_prompt()

# ── Import performance optimization module ──────────────
from PromptOptimizer import (
    get_optimizer, get_embedding_cache, get_context_cache,
    PromptOptimizer
)
optimizer = get_optimizer()
embedding_cache = get_embedding_cache()
context_cache = get_context_cache()

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


    messages = [{"role": "user", "content": user_q}]
 

    # ════════════════════════════════════════════════════════════════
    # OPTIMIZATION 2: Local LLM inference with better parameters
    # ════════════════════════════════════════════════════════════════
    
    try:
        # Ensure model is loaded
        load_model()

        # Efficient message formatting
        formatted_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted_messages.append(f"System: {content}")
            elif role == "user":
                formatted_messages.append(f"User: {content}")
            elif role == "assistant":
                formatted_messages.append(f"Assistant: {content}")

        # Combine messages into a single prompt
        prompt = "\n".join(formatted_messages) + "\nAssistant:"

        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        # Generate response with better parameters for quality
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,  # REDUCED from 256 for faster CPU generation
                temperature=0.7,
                do_sample=True,
                top_p=0.85,         # Slightly lower for speed
                top_k=40,           # Reduced from 50 for speed
                repetition_penalty=1.1,  # Reduced from 1.2 for speed
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant's response
        assistant_responses = full_response.split("Assistant:")
        reply = assistant_responses[-1].strip() if assistant_responses else full_response.strip()

        # Clean up the response
        if not reply:
            reply = "I apologize, but I couldn't generate a response. Please try again."

        print(f"[MODEL] Generated response ({len(reply)} chars)")

    except Exception as e:
        print(f"[ERROR] Model error: {e}")
        reply = f"[Model error: {str(e)[:100]}]"

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
    app.run(debug=False, port=5000)  # debug=False for production, avoids reloading