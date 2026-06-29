const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");
const newChatBtn = document.getElementById("newChatBtn");
const conversationList = document.getElementById("conversationList");
const searchBox = document.getElementById("searchChat");

// ---------------------------
// Add Message
// ---------------------------

function addMessage(sender, message) {

    const row = document.createElement("div");

    if (sender === "user") {

        row.className = "user-row";

        row.innerHTML = `
            <div class="user-message">
                ${message}
            </div>

            <div class="avatar">👤</div>
        `;

    }

    else {

        row.className = "bot-row";

        row.innerHTML = `
            <div class="avatar">🤖</div>

            <div class="bot-message">
                ${marked.parse(message)}
            </div>
        `;

    }

    chatBox.appendChild(row);

    // Highlight code blocks
    document.querySelectorAll("pre code").forEach((block) => {
        hljs.highlightElement(block);
    });

    chatBox.scrollTop = chatBox.scrollHeight;
}

// ---------------------------
// Send Message
// ---------------------------

async function sendMessage() {

    const message = messageInput.value.trim();

    if (message === "") return;

    addMessage("user", message);

    messageInput.value = "";

    typingIndicator.style.display = "block";

    chatBox.scrollTop = chatBox.scrollHeight;

    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: message
            })

        });

        const data = await response.json();

        // Simulate AI thinking
        setTimeout(() => {

            typingIndicator.style.display = "none";

            addMessage("bot", data.response);

            loadConversations();

        }, 800);

    }

    catch (error) {

        typingIndicator.style.display = "none";

        addMessage(
            "bot",
            "❌ Unable to connect to server."
        );

    }

}

// ---------------------------
// New Chat
// ---------------------------

newChatBtn.onclick = async function () {

    await fetch("/new_chat");

    chatBox.innerHTML = "";

    addMessage(
        "bot",
        "Hello 👋<br><br>How may I help you today?"
    );

    loadConversations();

};

// ---------------------------
// Load Conversations
// ---------------------------

async function loadConversations() {

    try {

        const response = await fetch("/conversations");

        const chats = await response.json();

        conversationList.innerHTML = "";

        chats.forEach(chat => {

            const div = document.createElement("div");

            div.className = "chat-item";

            div.innerHTML = chat.title || "New Chat";

            div.onclick = function () {

                loadMessages(chat.id);

            };

            conversationList.appendChild(div);

        });

    }

    catch(err){

        console.log(err);

    }

}

// ---------------------------
// Load Messages
// ---------------------------

async function loadMessages(id){

    const response = await fetch("/messages/" + id);

    const messages = await response.json();

    chatBox.innerHTML = "";

    messages.forEach(msg=>{

        addMessage(
            msg.sender,
            msg.message
        );

    });

}

// ---------------------------
// Search Chats
// ---------------------------

searchBox.addEventListener("keyup",function(){

    const value=this.value.toLowerCase();

    const chats=document.querySelectorAll(".chat-item");

    chats.forEach(chat=>{

        if(chat.innerText.toLowerCase().includes(value)){

            chat.style.display="block";

        }

        else{

            chat.style.display="none";

        }

    });

});

// ---------------------------
// Events
// ---------------------------

sendBtn.onclick = sendMessage;

messageInput.addEventListener("keypress", function(e){

    if(e.key==="Enter"){

        sendMessage();

    }

});

// ---------------------------
// Initial Load
// ---------------------------

loadConversations();