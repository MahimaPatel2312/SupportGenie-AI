from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

from intents import detect_intent
from faq import get_response
from gemini_service import get_ai_response

from database import (
    create_database,
    create_conversation,
    save_message,
    get_conversations,
    get_messages,
    get_recent_messages,
    get_dashboard_stats
)

from auth import register_user, login_user

# ----------------------------------------
# Flask Setup
# ----------------------------------------

app = Flask(__name__)
app.secret_key = "supportgenie_secret_key"

create_database()

# ----------------------------------------
# Home
# ----------------------------------------

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    return render_template(
        "chat.html",
        username=session["user_name"]
    )

# ----------------------------------------
# Register
# ----------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    success, message = register_user(name, email, password)

    if success:
        return redirect("/login")

    return render_template("register.html", message=message)

# ----------------------------------------
# Login
# ----------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"]
    password = request.form["password"]

    user = login_user(email, password)

    if user:
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        session.pop("conversation_id", None)

        return redirect("/")

    return render_template("login.html", message="Invalid Email or Password")

# ----------------------------------------
# Logout
# ----------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ----------------------------------------
# CHAT API (MAIN FIXED LOGIC)
# ----------------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    if "user_id" not in session:
        return jsonify({
            "response": "Please login first."
        }), 401

    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please enter a message."
        })

    # ----------------------------
    # Create conversation if needed
    # ----------------------------

    conversation_id = session.get("conversation_id")

    if conversation_id is None:
        conversation_id = create_conversation(
            session["user_id"],
            title="New Chat"
        )
        session["conversation_id"] = conversation_id

    # ----------------------------
    # Save user message
    # ----------------------------

    save_message(
        conversation_id,
        "user",
        message
    )

    # ----------------------------
    # Detect intent
    # ----------------------------

    intent = detect_intent(message)

    print("\n==============================")
    print("USER MESSAGE :", message)
    print("DETECTED INTENT :", intent)

    # ----------------------------
    # FAQ
    # ----------------------------

    reply = get_response(intent)

    print("FAQ RESPONSE :", reply)

    source = "FAQ"

    # ----------------------------
    # Gemini fallback
    # ----------------------------

    if reply is None:

        print("Calling Gemini...")

        history = get_recent_messages(conversation_id, limit=10)

        reply = get_ai_response(
            user_message=message,
            history=history
        )

        source = "Gemini"

        if intent == "unknown":
            intent = "AI"

    print("FINAL RESPONSE :", reply)
    print("==============================\n")

    # ----------------------------
    # Save bot reply
    # ----------------------------

    save_message(
        conversation_id,
        "bot",
        reply,
        intent,
        source
    )

    return jsonify({
        "response": reply,
        "intent": intent,
        "source": source
    })

# ----------------------------------------
# New Chat
# ----------------------------------------

@app.route("/new_chat")
def new_chat():

    if "user_id" not in session:
        return redirect("/login")

    session["conversation_id"] = create_conversation(session["user_id"])

    return jsonify({"success": True})

# ----------------------------------------
# Conversations
# ----------------------------------------

@app.route("/conversations")
def conversations():

    if "user_id" not in session:
        return jsonify([])

    chats = get_conversations(session["user_id"])

    return jsonify([
        {
            "id": c["id"],
            "title": c["title"] or "New Chat",
            "updated_at": c["updated_at"]
        }
        for c in chats
    ])

# ----------------------------------------
# Load Messages
# ----------------------------------------

@app.route("/messages/<int:conversation_id>")
def messages(conversation_id):

    if "user_id" not in session:
        return jsonify([])

    rows = get_messages(conversation_id)

    session["conversation_id"] = conversation_id

    return jsonify([
        {
            "sender": r["sender"],
            "message": r["message"],
            "timestamp": r["timestamp"]
        }
        for r in rows
    ])

# ----------------------------------------
# Dashboard
# ----------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    stats = get_dashboard_stats(session["user_id"])

    return render_template(
        "dashboard.html",
        username=session["user_name"],
        stats=stats
    )

# ----------------------------------------
# Run Server
# ----------------------------------------

if __name__ == "__main__":
    app.run(debug=True)