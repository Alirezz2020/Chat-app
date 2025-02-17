// static/js/group_chat.js
document.addEventListener("DOMContentLoaded", function() {
  const chatLog = document.getElementById("chat-log");
  const groupId = chatLog.getAttribute("data-group-id");
  const userUsername = chatLog.getAttribute("data-username");

  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const chatSocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/group/" + groupId + "/");

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
    console.error("Group chat socket closed unexpectedly");
  };

  document.getElementById("chat-message-send").addEventListener("click", function() {
    const inputDom = document.getElementById("chat-message-input");
    const message = inputDom.value;
    if (message.trim() === "") return;
    chatSocket.send(JSON.stringify({ "message": message }));
    inputDom.value = "";
  });
});
document.addEventListener("DOMContentLoaded", function() {
  const chatLog = document.getElementById("chat-log");
  const groupId = chatLog.getAttribute("data-group-id");
  const userUsername = chatLog.getAttribute("data-username");

  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const chatSocket = new WebSocket(wsScheme + "://" + window.location.host + "/ws/group/" + groupId + "/");

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
      <div class="message-body">
        <p>${data.message}</p>
        ${ data.attachment ? `<div class="attachment">
          ${ (data.attachment.toLowerCase().endsWith('.mp4')) ? `<video controls src="${data.attachment}"></video>` :
             (data.attachment.toLowerCase().endsWith('.mp3')) ? `<audio controls src="${data.attachment}"></audio>` :
             `<img src="${data.attachment}" alt="attachment">`
          }
        </div>` : "" }
      </div>
      <div class="message-meta"><span class="timestamp">${data.timestamp || ""}</span></div>
      <div class="message-status">
        ${data.sender === userUsername ? `<button class="edit-btn" data-message-id="${data.message_id}">Edit</button>
         <button class="delete-btn" data-message-id="${data.message_id}">Delete</button>` : ""}
      </div>
    `;
    chatLog.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  chatSocket.onclose = function(e) {
    console.error("Group chat socket closed unexpectedly");
  };

  document.getElementById("chat-message-send").addEventListener("click", function() {
    const inputDom = document.getElementById("chat-message-input");
    const fileInput = document.getElementById("chat-message-attachment");
    const message = inputDom.value;
    if (fileInput.files.length > 0) {
      const file = fileInput.files[0];
      const formData = new FormData();
      formData.append('file', file);

      fetch('/upload_file/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const fileUrl = data.file_url;
          chatSocket.send(JSON.stringify({ "message": message, "attachment": fileUrl }));
          inputDom.value = "";
          fileInput.value = "";
        } else {
          alert("File upload failed: " + data.error);
        }
      });
    } else if (message.trim() !== "") {
      chatSocket.send(JSON.stringify({ "message": message }));
      inputDom.value = "";
    }
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
