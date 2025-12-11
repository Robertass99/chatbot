const API_BASE_URL = "http://localhost:8000";

const chatWindow = document.getElementById("chat-window");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");
const typingIndicator = document.getElementById("typing-indicator");

let sessionId = localStorage.getItem("rb_session_id") || null;
let isWaiting = false;

function appendMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("msg", role === "user" ? "user" : "rick");

  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = role === "user" ? "Você" : "Rick";

  const bubble = document.createElement("div");
  bubble.className = "msg-bubble";
  bubble.innerHTML = text.replace(/\n/g, "<br>");

  wrapper.appendChild(meta);
  wrapper.appendChild(bubble);

  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {
  typingIndicator.classList.remove("hidden");
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function hideTyping() {
  typingIndicator.classList.add("hidden");
}

function appendError(text) {
  const wrapper = document.createElement("div");
  wrapper.classList.add("msg","rick");
  wrapper.innerHTML = `<div class="meta">Sistema</div><div class="msg-bubble" style="color:#ffb3b3">${text}</div>`;
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || isWaiting) return;
  appendMessage("user", text);
  userInput.value = "";
  isWaiting = true;
  showTyping();

  try {
    const payload = { message: text, session_id: sessionId };
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(()=>({detail:'Erro desconhecido'}));
      hideTyping();
      appendError("Erro na requisição: " + (err.detail || res.statusText));
      isWaiting = false;
      return;
    }

    const data = await res.json();
    if (data.session_id) {
      sessionId = data.session_id;
      localStorage.setItem("rb_session_id", sessionId);
    }
    hideTyping();
    appendMessage("rick", data.reply || "Hmm... nada por aqui.");
  } catch (e) {
    hideTyping();
    appendError("Erro ao conectar com o servidor: " + e.message);
  } finally {
    isWaiting = false;
  }
}

userInput.addEventListener("keydown", (ev) => {
  if (ev.key === "Enter" && !ev.shiftKey) {
    ev.preventDefault();
    sendMessage();
  }
});

sendBtn.addEventListener("click", sendMessage);

document.addEventListener("DOMContentLoaded", () => {
  if (chatWindow.children.length === 0) {
    appendMessage("rick", "Eai, precisando de alguma ajuda?");
    userInput.focus();
  }
});
