let ticketId = null;
const chat = document.getElementById("chat");

function addMessage(sender, text) {
  const div = document.createElement("div");
  div.className = "message";
  div.innerHTML = `<span class="${sender}">${sender}:</span> ${text}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById("messageInput");
  const text = input.value.trim();
  if (!text) return;

  addMessage("user", text);
  input.value = "";

  const payload = {
    message: text,
    ticket_id: ticketId
  };

  try {
    const res = await fetch("http://127.0.0.1:8000/execute-workflow", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await res.json();

    ticketId = data.workflow_result.ticket_id;

    addMessage("system", data.summary);

    if (data.workflow_result.status === "escalated") {
      addMessage("system", "This issue has been escalated to human support.");
    }

  } catch (err) {
    addMessage("system", "Error contacting backend.");
  }
}
