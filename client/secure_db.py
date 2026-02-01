import json
import os

KEY_FILE = "client_keys.json"

def save_keys(username, pub_k, priv_k):
    data = {}
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, 'r') as f: data = json.load(f)
        except: pass
    data[username] = {"pub": pub_k, "priv": priv_k}
    with open(KEY_FILE, 'w') as f: json.dump(data, f)

def load_keys(username):
    if not os.path.exists(KEY_FILE): return None, None
    try:
        with open(KEY_FILE, 'r') as f:
            user_data = json.load(f).get(username)
            if user_data: return user_data['pub'], user_data['priv']
    except: pass
    return None, None