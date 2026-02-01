from flask import Flask, render_template, request, session, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import json
import os
import sys
import uuid

sys.path.append(os.getcwd())
from core.crypto_utils import hash_password, verify_password, AESCipher
from core.paillier import SimplePaillier
from core.stego import Steganography
from database import DatabaseManager

app = Flask(__name__)
app.secret_key = "SecretKeyForSession"
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'txt', 'pdf', 'doc', 'docx', 'zip', 'rar'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

with open('config.json', 'r') as f: CONFIG = json.load(f)
db = DatabaseManager(CONFIG['db_path'])

user_keys = {}
def init_user_keys(username):
    if username not in user_keys:
        aes = AESCipher(CONFIG['shared_secret'])
        user_keys[username] = {'aes': aes}
    return user_keys[username]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index(): return redirect(url_for('chat')) if 'username' in session else render_template('login.html')

@app.route('/chat')
def chat(): return render_template('chat.html', username=session['username']) if 'username' in session else redirect(url_for('index'))

# === 1. 隐写术 ===
@app.route('/api/stego_hide', methods=['POST'])
def stego_hide():
    if 'image' not in request.files: return jsonify({'status':'error'})
    file = request.files['image']
    text = request.form.get('text', '')
    unique = "stego_" + str(uuid.uuid4()) + ".png"
    path = os.path.join(app.config['UPLOAD_FOLDER'], unique)
    file.save(path + ".tmp")
    
    stego = Steganography()
    if stego.hide(path + ".tmp", text, path):
        os.remove(path + ".tmp")
        return jsonify({'status': 'ok', 'url': f'/static/uploads/{unique}', 'msg_type': 'image', 'file_name': 'secret.png'})
    return jsonify({'status': 'error'})

@app.route('/api/stego_extract', methods=['POST'])
def stego_extract():
    url = request.json.get('url')
    if not url: return jsonify({'status':'error'})
    path = os.path.join(app.config['UPLOAD_FOLDER'], url.split('/')[-1])
    return jsonify({'status': 'ok', 'text': Steganography().extract(path)})

# === 2. 隐私计算 ===
@app.route('/api/client_mock_encrypt', methods=['POST'])
def client_mock_encrypt():
    values = request.json.get('values')
    pai = SimplePaillier()
    pub, priv = pai.generate_keys(128)
    return jsonify({'status': 'ok', 'public_key': pub, 'private_key': priv, 'ciphertexts': [pai.encrypt(pub, int(v)) for v in values]})

@app.route('/api/privacy_calc', methods=['POST'])
def privacy_calc():
    pub = request.json.get('public_key')
    ciphers = request.json.get('ciphertexts')
    n_sq = int(pub['n']) ** 2
    res = 1
    for c in ciphers: res = (res * int(c)) % n_sq
    return jsonify({'status': 'ok', 'encrypted_sum': str(res)})

@app.route('/api/client_mock_decrypt', methods=['POST'])
def client_mock_decrypt():
    pub = request.json.get('public_key')
    priv = request.json.get('private_key')
    c = request.json.get('encrypted_sum')
    return jsonify({'result': SimplePaillier().decrypt(pub, priv, c)})

# === 3. SSE 搜索 ===
@app.route('/api/search_sse', methods=['POST'])
def search_sse():
    if 'username' not in session: return jsonify([])
    trapdoor = request.json.get('trapdoor')
    room = "_".join(sorted([session['username'], request.json.get('target')]))
    results = db.search_encrypted(trapdoor, room)
    
    keys = init_user_keys(session['username'])
    decrypted = []
    for msg in results:
        try:
            pt = keys['aes'].decrypt(msg['content_enc'])
            decrypted.append({**msg, "content": pt, "is_encrypted": False})
        except: pass
    return jsonify(decrypted)

# === 基础功能 ===
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'status': 'error'})
    file = request.files['file']
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique = str(uuid.uuid4()) + "." + ext
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique))
        return jsonify({'status': 'ok', 'url': f'/static/uploads/{unique}', 'msg_type': 'image' if ext in ['png','jpg','jpeg','gif'] else 'file', 'original_name': file.filename})
    return jsonify({'status': 'error'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    creds = db.get_user_credentials(data.get('username'))
    if creds and verify_password(creds[0], creds[1], data.get('password')):
        session['username'] = data.get('username')
        init_user_keys(data.get('username'))
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "msg": "Fail"})

@app.route('/api/register', methods=['POST'])
def register():
    key, salt = hash_password(request.json.get('password'))
    if db.register_user(request.json.get('username'), key, salt): return jsonify({"status": "ok"})
    return jsonify({"status": "error", "msg": "Exists"})

@app.route('/api/logout', methods=['POST'])
def logout(): session.pop('username', None); return jsonify({"status": "ok"})

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session: return jsonify({"status":"error"}), 403
    user = session['username']
    if request.method=='GET':
        d = db.get_user_profile(user)
        return jsonify(d if d else {"nickname":user, "signature":"", "avatar_color":"#3498db"})
    db.update_user_profile(user, request.json['nickname'], request.json['signature'], request.json['avatar_color'])
    return jsonify({"status":"ok"})

@app.route('/api/friends')
def get_friends_list(): return jsonify(db.get_friends(session.get('username')) if 'username' in session else [])

@app.route('/api/requests', methods=['GET', 'POST'])
def friend_requests():
    user = session['username']
    if request.method == 'GET': return jsonify(db.get_pending_requests(user))
    if db.send_friend_request(user, request.json.get('target')):
        socketio.emit('new_request_notify', {'from': user}, room=request.json.get('target'))
        return jsonify({"status": "ok", "msg": "Sent"})
    return jsonify({"status": "error"})

@app.route('/api/handle_request', methods=['POST'])
def handle_request():
    if db.handle_request(request.json['req_id'], request.json['action'], session['username']): return jsonify({"status": "ok"})
    return jsonify({"status": "error"})

# === Socket ===
@socketio.on('connect')
def on_connect():
    if 'username' in session: join_room(session['username']); init_user_keys(session['username'])

@socketio.on('join_chat')
def on_join(data):
    me = session['username']
    room = "_".join(sorted([me, data['target']]))
    join_room(room)
    
    keys = init_user_keys(me)
    decrypted = []
    for msg in db.get_room_history(room):
        try:
            pt = keys['aes'].decrypt(msg['content_enc'])
            decrypted.append({**msg, "content": pt, "is_encrypted": False})
        except: decrypted.append({**msg, "content": "[Fail]", "is_encrypted": True})
    emit('history_messages', decrypted)

@socketio.on('send_message')
def on_send(data):
    sender = session['username']
    room = "_".join(sorted([sender, data['target']]))
    keys = init_user_keys(sender)
    
    enc_content = keys['aes'].encrypt(data['content'])
    msg_id = db.store_message(room, sender, enc_content, data.get('msg_type','text'), data.get('file_name'))
    
    if data.get('msg_type') == 'text' and data.get('search_indexes'):
        db.add_search_index(msg_id, data['search_indexes'])
    
    emit('new_message', {
        "id": msg_id, "sender": sender, "content": data['content'],
        "msg_type": data.get('msg_type','text'), "file_name": data.get('file_name'),
        "is_encrypted": False, "room": room
    }, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=9999, debug=False, allow_unsafe_werkzeug=True)