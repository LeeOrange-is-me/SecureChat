const socket = io();
let currentTarget = null;

// --- 登录/注册 ---
async function doLogin() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const res = await fetch('/api/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p})
    });
    const data = await res.json();
    if (data.status === 'ok') window.location.reload();
    else alert(data.msg);
}

async function doRegister() {
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    const res = await fetch('/api/register', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u, password: p})
    });
    const data = await res.json();
    alert(data.status === 'ok' ? "注册成功" : data.msg);
}

// --- 初始化与好友 ---
if (window.location.pathname === '/chat') {
    loadFriends();
    checkRequests();

    socket.on('new_request_notify', () => {
        alert("收到新的好友请求！");
        checkRequests();
    });

    socket.on('new_message', (data) => {
        // 如果当前正在和发送者聊天，或者是我自己发的消息
        if (data.room === getRoomName(currentTarget) || data.sender === '{{ username }}') { // 这里简单判断
            appendMessage(data);
        }
    });

    socket.on('history_messages', (msgs) => {
        document.getElementById('messages').innerHTML = '';
        msgs.forEach(m => appendMessage({
            sender: m.sender,
            content: "[历史加密消息] " + m.content_enc.substring(0, 10) + "...", // 演示用
            is_encrypted: true
        }));
    });
}

async function loadFriends() {
    const res = await fetch('/api/friends');
    const list = await res.json();
    const container = document.getElementById('friend-list');
    container.innerHTML = '';
    list.forEach(f => {
        const div = document.createElement('div');
        div.className = 'friend-item';
        div.innerText = f;
        div.onclick = () => selectFriend(f, div);
        container.appendChild(div);
    });
}

function selectFriend(name, el) {
    currentTarget = name;
    document.getElementById('chat-header').innerText = `正在与 ${name} 聊天`;
    document.querySelectorAll('.friend-item').forEach(e => e.classList.remove('active'));
    el.classList.add('active');
    
    // 启用输入框
    document.getElementById('msg-input').disabled = false;
    document.getElementById('send-btn').disabled = false;
    document.getElementById('messages').innerHTML = ''; // 清空之前

    // 加入房间
    socket.emit('join_chat', {target: name});
}

function sendMessage() {
    const input = document.getElementById('msg-input');
    const text = input.value;
    if (!text || !currentTarget) return;
    
    socket.emit('send_message', {target: currentTarget, content: text});
    input.value = '';
}

function appendMessage(data) {
    // 这里简单判断是否是自己
    // 注意：实际项目中不要在JS里硬编码 Session 值，这里为简化演示逻辑
    // 通过 CSS 类区分
    const isMe = (data.sender === document.querySelector('.header h3').innerText.split(': ')[1]);
    
    const div = document.createElement('div');
    div.className = `msg ${isMe ? 'sent' : 'received'}`;
    div.innerHTML = `<div class="msg-info">${data.sender} ${data.is_encrypted ? '🔒' : ''}</div>${data.content}`;
    document.getElementById('messages').appendChild(div);
    // 滚动到底部
    const area = document.getElementById('messages');
    area.scrollTop = area.scrollHeight;
}

// --- 好友请求逻辑 ---
function showAddFriend() { document.getElementById('modal-add').classList.remove('hidden'); }
function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

async function sendFriendRequest() {
    const target = document.getElementById('search-friend').value;
    const res = await fetch('/api/requests', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({target: target})
    });
    const data = await res.json();
    alert(data.msg);
    closeModal('modal-add');
}

async function checkRequests() {
    const res = await fetch('/api/requests');
    const reqs = await res.json();
    const btn = document.getElementById('req-btn');
    btn.innerText = reqs.length > 0 ? `验证消息 (${reqs.length})` : "验证消息";
    
    const list = document.getElementById('req-list');
    list.innerHTML = '';
    reqs.forEach(r => {
        const div = document.createElement('div');
        div.className = 'req-item';
        div.innerHTML = `<span>${r.from_user} 请求添加好友</span>
            <div>
                <button onclick="handleReq(${r.id}, 'accept')">同意</button>
                <button onclick="handleReq(${r.id}, 'reject')" class="secondary">拒绝</button>
            </div>`;
        list.appendChild(div);
    });
}

function showRequests() { document.getElementById('modal-req').classList.remove('hidden'); }

async function handleReq(id, action) {
    await fetch('/api/handle_request', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({req_id: id, action: action})
    });
    closeModal('modal-req');
    checkRequests();
    loadFriends(); // 刷新好友列表
}

function getRoomName(target) {
    // 简单的辅助函数，不用于安全校验
    return target; 
}

// 占位功能
function doSearch() { alert("调用后端 sse_utils 进行密态搜索... (Web演示版)"); }
function doPrivacy() { alert("调用后端 paillier 进行薪资计算... (Web演示版)"); }