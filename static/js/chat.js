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
// static/js/chat.js
document.addEventListener("DOMContentLoaded", function() {
  const chatLog = document.getElementById("chat-log");
  const friendId = chatLog.getAttribute("data-friend-id");
  const userUsername = chatLog.getAttribute("data-username");

  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const chatSocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/chat/" + friendId + "/");

  chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + (data.sender === userUsername ? "own" : "other");
    messageDiv.innerHTML = `
      <div class="message-header">
        ${data.sender === userUsername ? 
          `<div class="message-info own-info">
             <a href="/profile/${data.sender}/" class="username">YOU</a>
             <img src="/static/img/default.png" class="profile-thumb">
           </div>` :
          `<div class="message-info other-info">
             <img src="/static/img/default.png" class="profile-thumb">
             <a href="/profile/${data.sender}/" class="username">${data.sender}</a>
           </div>`
        }
      </div>
      <div class="message-body"><p>${data.message}</p></div>
      <div class="message-status">
        ${data.sender === userUsername ? `<button class="edit-btn" data-message-id="${data.message_id}">Edit</button>
         <button class="delete-btn" data-message-id="${data.message_id}">Delete</button>` : ""}
      </div>
    `;
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
});
// static/js/chat.js
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
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + (data.sender === userUsername ? "own" : "other");
    messageDiv.innerHTML = `
      <div class="message-header">
        ${
          data.sender === userUsername
          ? `<div class="message-info own-info">
               <a href="/profile/${data.sender}/" class="username">YOU</a>
               <img src="/static/img/default.png" class="profile-thumb">
             </div>`
          : `<div class="message-info other-info">
               <img src="/static/img/default.png" class="profile-thumb">
               <a href="/profile/${data.sender}/" class="username">${data.sender}</a>
             </div>`
        }
      </div>
      <div class="message-body"><p>${data.message}</p></div>
      <div class="message-meta"><span class="timestamp">${data.timestamp || ""}</span></div>
      <div class="message-status">
        ${
          data.sender === userUsername 
          ? `<button class="edit-btn" data-message-id="${data.message_id}">Edit</button>
             <button class="delete-btn" data-message-id="${data.message_id}">Delete</button>`
          : ""
        }
      </div>
    `;
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

  // Event delegation for edit and delete buttons:
  chatLog.addEventListener("click", function(e) {
    if (e.target.classList.contains("edit-btn")) {
      const messageId = e.target.getAttribute("data-message-id");
      const newContent = prompt("Edit your message:");
      if (newContent) {
        fetch(`/edit_message/${messageId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
          },
          body: JSON.stringify({ content: newContent })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert("Message edited successfully.");
            location.reload();
          } else {
            alert("Failed to edit message.");
          }
        });
      }
    }
    if (e.target.classList.contains("delete-btn")) {
      const messageId = e.target.getAttribute("data-message-id");
      if (confirm("Are you sure you want to delete this message?")) {
        fetch(`/delete_message/${messageId}/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert("Message deleted successfully.");
            location.reload();
          } else {
            alert("Failed to delete message.");
          }
        });
      }
    }
  });

  // Helper function to get CSRF token from cookies
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
