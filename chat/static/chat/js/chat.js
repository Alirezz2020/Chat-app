// ChatProject/chat/static/chat/js/chat.js
document.addEventListener("DOMContentLoaded", function() {
    const chatLog = document.getElementById("chat-log");
    const friendId = chatLog.getAttribute("data-friend-id");
    const userUsername = chatLog.getAttribute("data-username");

   const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
const chatSocket = new WebSocket(
    wsScheme + "://" + window.location.host + "/ws/chat/" + friendId + "/"
);


    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const message = data.message;
        const sender = data.sender;
        const messageDiv = document.createElement("div");

        if (sender === userUsername) {
            messageDiv.className = "user-message";
            messageDiv.innerHTML = `<p>${message}</p><div class="message-ticks">✓</div>`;
        } else {
            messageDiv.className = "friend-message";
            messageDiv.innerHTML = `<p>${message}</p>`;
        }
        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error("Chat socket closed unexpectedly");
    };

    document.getElementById("chat-message-send").addEventListener("click", function() {
        const inputDom = document.getElementById("chat-message-input");
        const message = inputDom.value;
        if (message.trim() === "") return;
        chatSocket.send(JSON.stringify({ "message": message }));
        inputDom.value = "";
    });

    document.getElementById("chat-message-input").addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            document.getElementById("chat-message-send").click();
        }
    });
});
