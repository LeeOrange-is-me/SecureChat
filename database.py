import sqlite3
import os
import time
import hashlib
import hmac

class DatabaseManager:
    def __init__(self, db_path):
        folder = os.path.dirname(db_path)
        # 强制使用 final 数据库
        new_db_path = os.path.join(folder, 'secure_chat_final.db')
        os.makedirs(folder, exist_ok=True)
        self.conn = sqlite3.connect(new_db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password_hash BLOB, salt BLOB,
            nickname TEXT, signature TEXT, avatar_color TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS friends (user TEXT, friend TEXT, UNIQUE(user, friend))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT, from_user TEXT, to_user TEXT, status INTEGER DEFAULT 0, UNIQUE(from_user, to_user)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            sender TEXT,
            content_enc TEXT,
            msg_type TEXT DEFAULT 'text',
            file_name TEXT,
            timestamp REAL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS search_index (
            trapdoor TEXT,
            message_id INTEGER
        )''')
        self.conn.commit()

    # --- SSE 搜索核心逻辑 ---
    def add_search_index(self, message_id, trapdoors):
            if not trapdoors: return
            cursor = self.conn.cursor()
            for trapdoor in trapdoors:
                # 直接存入前端传来的哈希值
                cursor.execute("INSERT INTO search_index (trapdoor, message_id) VALUES (?, ?)", (trapdoor, message_id))
            self.conn.commit()
    # [关键修改] 返回 ID
    def search_encrypted(self, query_trapdoor, room):
        cursor = self.conn.cursor()
        sql = """
            SELECT m.id, m.sender, m.content_enc, m.msg_type, m.file_name, m.timestamp
            FROM messages m
            JOIN search_index idx ON m.id = idx.message_id
            WHERE idx.trapdoor = ? AND m.room = ?
            ORDER BY m.timestamp DESC
        """
        cursor.execute(sql, (query_trapdoor, room))
        return [{"id": r[0], "sender": r[1], "content_enc": r[2], "msg_type": r[3], "file_name": r[4], "timestamp": r[5]} for r in cursor.fetchall()]

    # --- 常规数据库操作 ---
    def store_message(self, room, sender, content_enc, msg_type='text', file_name=None):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO messages (room, sender, content_enc, msg_type, file_name, timestamp) VALUES (?, ?, ?, ?, ?, ?)", 
                       (room, sender, content_enc, msg_type, file_name, time.time()))
        msg_id = cursor.lastrowid
        self.conn.commit()
        return msg_id

    # [关键修改] 返回 ID
    def get_room_history(self, room):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, sender, content_enc, msg_type, file_name, timestamp FROM messages WHERE room=? ORDER BY timestamp ASC LIMIT 100", (room,))
        return [{"id": r[0], "sender": r[1], "content_enc": r[2], "msg_type": r[3], "file_name": r[4], "timestamp": r[5]} for r in cursor.fetchall()]

    # ... (用户/好友逻辑保持不变) ...
    def register_user(self, username, pwd_hash, salt):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash, salt, nickname, signature, avatar_color) VALUES (?, ?, ?, ?, ?, ?)", 
                           (username, pwd_hash, salt, username, "这个人很懒...", "#3498db"))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False

    def get_user_profile(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT nickname, signature, avatar_color FROM users WHERE username=?", (username,))
        res = cursor.fetchone()
        if res: return {"nickname": res[0], "signature": res[1], "avatar_color": res[2]}
        return None

    def update_user_profile(self, username, nickname, signature, avatar_color):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE users SET nickname=?, signature=?, avatar_color=? WHERE username=?", (nickname, signature, avatar_color, username))
        self.conn.commit()
        return True

    def get_user_credentials(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
        return cursor.fetchone()

    def send_friend_request(self, from_user, to_user):
        if from_user == to_user: return False
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM friends WHERE user=? AND friend=?", (from_user, to_user))
        if cursor.fetchone(): return False 
        try:
            cursor.execute("INSERT INTO friend_requests (from_user, to_user, status) VALUES (?, ?, 0)", (from_user, to_user))
            self.conn.commit()
            return True
        except: return False

    def get_pending_requests(self, user):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, from_user FROM friend_requests WHERE to_user=? AND status=0", (user,))
        return [{"id": r[0], "from_user": r[1]} for r in cursor.fetchall()]

    def handle_request(self, req_id, action, current_user):
        cursor = self.conn.cursor()
        cursor.execute("SELECT from_user, to_user FROM friend_requests WHERE id=? AND to_user=?", (req_id, current_user))
        req = cursor.fetchone()
        if not req: return False
        sender, receiver = req
        if action == 'accept':
            cursor.execute("INSERT OR IGNORE INTO friends (user, friend) VALUES (?, ?)", (sender, receiver))
            cursor.execute("INSERT OR IGNORE INTO friends (user, friend) VALUES (?, ?)", (receiver, sender))
            cursor.execute("UPDATE friend_requests SET status=1 WHERE id=?", (req_id,))
        else:
            cursor.execute("UPDATE friend_requests SET status=2 WHERE id=?", (req_id,))
        self.conn.commit()
        return True

    def get_friends(self, user):
        cursor = self.conn.cursor()
        cursor.execute("SELECT friend FROM friends WHERE user=?", (user,))
        return [row[0] for row in cursor.fetchall()]