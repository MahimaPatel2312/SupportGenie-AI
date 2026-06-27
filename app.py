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

from database import (
    create_database,
    create_conversation,
    save_message,
    get_conversations,
    get_messages,
    get_dashboard_stats
)

from auth import (
    register_user,
    login_user
)

# ----------------------------------------
# Flask Configuration
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

    success, message = register_user(
        name,
        email,
        password
    )

    if success:
        return redirect("/login")

    return render_template(
        "register.html",
        message=message
    )


# ----------------------------------------
# Login
# ----------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form["email"]
    password = request.form["password"]

    user = login_user(
        email,
        password
    )

    if user:

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        return redirect("/")

    return render_template(
        "login.html",
        message="Invalid Email or Password"
    )


# ----------------------------------------
# Logout
# ----------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ----------------------------------------
# Chat API
# ----------------------------------------

@app.route("/chat", methods=["POST"])
def chat():

    if "user_id" not in session:

        return jsonify({

            "response": "Please login."

        }), 401

    data = request.get_json()

    message = data.get("message", "").strip()

    if message == "":

        return jsonify({

            "response": "Please enter a message."

        })

    # --------------------------
    # Create Conversation
    # --------------------------

    if "conversation_id" not in session:

        conversation_id = create_conversation(
            session["user_id"]
        )

        session["conversation_id"] = conversation_id

    conversation_id = session["conversation_id"]

    # Save user message

    save_message(

        conversation_id,

        "user",

        message

    )

    # Detect intent

    intent = detect_intent(message)

    # FAQ reply

    reply = get_response(intent)

    # Save bot reply

    save_message(

        conversation_id,

        "bot",

        reply,

        intent,

        "FAQ"

    )

    return jsonify({

        "response": reply,

        "intent": intent

    })


# ----------------------------------------
# New Conversation
# ----------------------------------------

@app.route("/new_chat")
def new_chat():

    if "user_id" not in session:

        return redirect("/login")

    conversation_id = create_conversation(

        session["user_id"]

    )

    session["conversation_id"] = conversation_id

    return jsonify({

        "success": True

    })


# ----------------------------------------
# Conversation List
# ----------------------------------------

@app.route("/conversations")
def conversations():

    if "user_id" not in session:

        return jsonify([])

    chats = get_conversations(

        session["user_id"]

    )

    result = []

    for chat in chats:

        result.append({

            "id": chat["id"],

            "title": chat["title"],

            "updated_at": chat["updated_at"]

        })

    return jsonify(result)


# ----------------------------------------
# Load Messages
# ----------------------------------------

@app.route("/messages/<int:conversation_id>")
def messages(conversation_id):

    rows = get_messages(conversation_id)

    result = []

    for row in rows:

        result.append({

            "sender": row["sender"],

            "message": row["message"],

            "timestamp": row["timestamp"]

        })

    return jsonify(result)


# ----------------------------------------
# Dashboard
# ----------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    stats = get_dashboard_stats(

        session["user_id"]

    )

    return render_template(

        "dashboard.html",

        username=session["user_name"],

        stats=stats

    )


# ----------------------------------------
# Run
# ----------------------------------------

if __name__ == "__main__":

    app.run(debug=True)