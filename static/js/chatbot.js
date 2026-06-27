const chatBox = document.getElementById("chatBox");
const sendBtn = document.getElementById("sendBtn");
const messageInput = document.getElementById("message");
const newChatBtn = document.getElementById("newChatBtn");

sendBtn.addEventListener("click", sendMessage);

messageInput.addEventListener("keypress", function(event){
    if(event.key==="Enter"){
        sendMessage();
    }
});

newChatBtn.addEventListener("click", newChat);

function getCurrentTime(){

    return new Date().toLocaleTimeString([],{
        hour:"2-digit",
        minute:"2-digit"
    });

}

async function sendMessage(){

    const message = messageInput.value.trim();

    if(message==="") return;

    addUserMessage(message);

    messageInput.value="";

    showTyping();

    try{

        const response = await fetch("/chat",{

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({
                message:message
            })

        });

        const data = await response.json();

        removeTyping();

        addBotMessage(data.response);

    }

    catch(error){

        removeTyping();

        addBotMessage("❌ Unable to connect to server.");

        console.error(error);

    }

}

function addUserMessage(message){

    const userContainer=document.createElement("div");

    userContainer.className="user-message-container";

    userContainer.innerHTML=`

        <div class="user-message">

            ${message}

            <div class="timestamp">

                ${getCurrentTime()}

            </div>

        </div>

        <div class="avatar user-avatar">

            👤

        </div>

    `;

    chatBox.appendChild(userContainer);

    chatBox.scrollTop=chatBox.scrollHeight;

}

function showTyping(){

    const typing=document.createElement("div");

    typing.className="bot-message-container";

    typing.id="typing";

    typing.innerHTML=`

        <div class="avatar">

            🤖

        </div>

        <div class="typing">

            <div class="dot"></div>

            <div class="dot"></div>

            <div class="dot"></div>

        </div>

    `;

    chatBox.appendChild(typing);

    chatBox.scrollTop=chatBox.scrollHeight;

}

function removeTyping(){

    const typing=document.getElementById("typing");

    if(typing){

        typing.remove();

    }

}

function addBotMessage(message){

    const botContainer=document.createElement("div");

    botContainer.className="bot-message-container";

    botContainer.innerHTML=`

        <div class="avatar">

            🤖

        </div>

        <div class="bot-message">

            ${message}

            <div class="timestamp">

                ${getCurrentTime()}

            </div>

        </div>

    `;

    chatBox.appendChild(botContainer);

    chatBox.scrollTop=chatBox.scrollHeight;

}

function newChat(){

    chatBox.innerHTML=`

        <div class="bot-message-container">

            <div class="avatar">

                🤖

            </div>

            <div class="bot-message">

                👋 Hello!

                <br><br>

                How can I help you today?

                <div class="timestamp">

                    ${getCurrentTime()}

                </div>

            </div>

        </div>

    `;

}