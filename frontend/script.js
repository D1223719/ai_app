const API_BASE = '/api';

let currentSessionId = null;

// DOM Elements
const sessionsListEl = document.getElementById('sessions-list');
const messagesContainerEl = document.getElementById('messages-container');
const chatInputEl = document.getElementById('chat-input');
const sendBtnEl = document.getElementById('send-btn');
const newSessionBtnEl = document.getElementById('new-session-btn');
const uploadBtnEl = document.getElementById('upload-btn');
const fileUploadEl = document.getElementById('file-upload');
const currentSessionTitleEl = document.getElementById('current-session-title');

// Modal Elements
const modalEl = document.getElementById('new-session-modal');
const closeModalBtn = document.querySelector('.close-modal');
const createSessionConfirmBtn = document.getElementById('create-session-confirm');
const sessionTitleInput = document.getElementById('session-title');

// Event Listeners
newSessionBtnEl.addEventListener('click', () => {
    modalEl.classList.add('show');
    sessionTitleInput.focus();
});

closeModalBtn.addEventListener('click', () => {
    modalEl.classList.remove('show');
});

createSessionConfirmBtn.addEventListener('click', async () => {
    const title = sessionTitleInput.value.trim();
    if (!title) return;
    
    try {
        const res = await fetch(`${API_BASE}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title })
        });
        const data = await res.json();
        modalEl.classList.remove('show');
        sessionTitleInput.value = '';
        await loadSessions();
        selectSession(data.id, data.title);
    } catch (err) {
        console.error('Error creating session', err);
    }
});

uploadBtnEl.addEventListener('click', () => {
    fileUploadEl.click();
});

fileUploadEl.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file || !currentSessionId) return;

    const fileType = prompt("請輸入文件類型 (例如: resume_base 或 job_description):", "resume_base");
    if (!fileType) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    uploadBtnEl.disabled = true;
    uploadBtnEl.innerHTML = '<i class="ri-loader-4-line ri-spin"></i>';

    try {
        const res = await fetch(`${API_BASE}/sessions/${currentSessionId}/upload`, {
            method: 'POST',
            body: formData
        });
        await loadMessages(currentSessionId);
    } catch (err) {
        console.error('Upload failed', err);
    } finally {
        uploadBtnEl.disabled = false;
        uploadBtnEl.innerHTML = '<i class="ri-attachment-2"></i>';
        fileUploadEl.value = '';
    }
});

chatInputEl.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    sendBtnEl.disabled = this.value.trim() === '';
});

chatInputEl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtnEl.addEventListener('click', sendMessage);

// Functions
async function loadSessions() {
    try {
        const res = await fetch(`${API_BASE}/sessions`);
        const sessions = await res.json();
        
        sessionsListEl.innerHTML = '';
        sessions.forEach(session => {
            const div = document.createElement('div');
            div.className = `session-item ${session.id === currentSessionId ? 'active' : ''}`;
            div.innerHTML = `<i class="ri-message-3-line"></i> <span>${session.title}</span>`;
            div.onclick = () => selectSession(session.id, session.title);
            sessionsListEl.appendChild(div);
        });
    } catch (err) {
        console.error('Error loading sessions', err);
    }
}

async function selectSession(id, title) {
    currentSessionId = id;
    currentSessionTitleEl.textContent = title;
    
    Array.from(sessionsListEl.children).forEach(el => el.classList.remove('active'));
    await loadSessions();

    chatInputEl.disabled = false;
    uploadBtnEl.disabled = false;

    await loadMessages(id);
}

async function loadMessages(sessionId) {
    try {
        const res = await fetch(`${API_BASE}/sessions/${sessionId}/messages`);
        const messages = await res.json();
        
        messagesContainerEl.innerHTML = '';
        if (messages.length === 0) {
            messagesContainerEl.innerHTML = `
                <div class="welcome-screen">
                    <i class="ri-file-text-line"></i>
                    <h2>開始與顧問對話</h2>
                    <p>請先點擊上方迴紋針上傳您的履歷或 JD，或者直接輸入訊息。</p>
                </div>
            `;
            return;
        }

        messages.forEach(msg => appendMessage(msg));
        scrollToBottom();
    } catch (err) {
        console.error('Error loading messages', err);
    }
}

function appendMessage(msg) {
    const div = document.createElement('div');
    div.className = `message ${msg.role}`;
    
    if (msg.role === 'system') {
        div.innerHTML = `<span>${msg.content}</span>`;
    } else {
        const content = msg.role === 'assistant' ? marked.parse(msg.content) : msg.content;
        div.innerHTML = `<div class="bubble">${content}</div>`;
    }
    
    messagesContainerEl.appendChild(div);
}

async function sendMessage() {
    const text = chatInputEl.value.trim();
    if (!text || !currentSessionId) return;

    chatInputEl.value = '';
    chatInputEl.style.height = 'auto';
    sendBtnEl.disabled = true;
    
    appendMessage({ role: 'user', content: text });
    scrollToBottom();

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading';
    loadingDiv.innerHTML = `<div class="bubble"><i class="ri-loader-4-line ri-spin"></i> 思考中...</div>`;
    messagesContainerEl.appendChild(loadingDiv);
    scrollToBottom();

    try {
        const res = await fetch(`${API_BASE}/sessions/${currentSessionId}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: text })
        });
        const data = await res.json();
        
        messagesContainerEl.removeChild(loadingDiv);
        appendMessage(data.assistant_message);
        scrollToBottom();
    } catch (err) {
        console.error('Chat error', err);
        messagesContainerEl.removeChild(loadingDiv);
        alert('發送訊息失敗，請稍後再試。');
    }
}

function scrollToBottom() {
    messagesContainerEl.scrollTop = messagesContainerEl.scrollHeight;
}

// Init
loadSessions();
