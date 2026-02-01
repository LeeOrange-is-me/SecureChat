import socket
import threading
import json
import sys
import os
import traceback # 引入这个库来查看详细报错

# --- 路径设置 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from core.paillier import SimplePaillier
from core.crypto_utils import hash_password, verify_password
from server.database import DatabaseManager

# 读取配置
config_path = os.path.join(root_dir, 'config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

# 初始化数据库
db_manager = DatabaseManager(os.path.join(root_dir, CONFIG['db_path']))

online_clients = {} 
message_store = []  
search_index = {}   
salary_data = []    

def handle_client(conn, addr):
    print(f"[SERVER] Connection from {addr}")
    current_user = None
    
    try:
        while True:
            msg = conn.recv(8192).decode('utf-8')
            if not msg: break
            
            data = json.loads(msg)
            action = data.get('action')

            if action == 'REGISTER':
                print(f"[SERVER] Processing Register: {data['username']}")
                # 这里的 password 可能是字符串，hash_password 内部需要处理
                p_hash, salt = hash_password(data['password'])
                success = db_manager.register_user(data['username'], p_hash, salt)
                resp = {"status": "OK" if success else "FAIL", "msg": "注册成功" if success else "用户已存在"}
                conn.send(json.dumps(resp).encode())
                print(f"[SERVER] Register result sent.")

            elif action == 'LOGIN':
                uname = data['username']
                print(f"[SERVER] Processing Login: {uname}")
                creds = db_manager.get_user_credentials(uname)
                if creds and verify_password(creds[0], creds[1], data['password']):
                    current_user = uname
                    online_clients[current_user] = conn
                    conn.send(json.dumps({"status": "OK", "msg": "登录成功"}).encode())
                else:
                    conn.send(json.dumps({"status": "FAIL", "msg": "用户名或密码错误"}).encode())

            # --- 登录后的功能 ---
            elif not current_user:
                conn.send(json.dumps({"status": "FAIL", "msg": "请先登录"}).encode())
                continue

            elif action == 'GET_FRIENDS':
                friends = db_manager.get_friends(current_user)
                conn.send(json.dumps({"status": "OK", "friends": friends, "type": "FRIEND_LIST"}).encode())

            elif action == 'ADD_FRIEND':
                success = db_manager.add_friend(current_user, data['friend_name'])
                conn.send(json.dumps({"status": "OK", "msg": "添加成功" if success else "用户不存在"}).encode())

            elif action == 'SEND_MSG':
                target = data.get('target', 'ALL')
                cipher = data['cipher_text']
                msg_id = len(message_store)
                message_store.append({"sender": current_user, "target": target, "content": cipher})
                
                for td in data.get('trapdoors', []):
                    if td not in search_index: search_index[td] = []
                    search_index[td].append(msg_id)

                conn.send(json.dumps({"type": "MSG_ACK", "target": target, "content": cipher}).encode())

                fwd_msg = {"type": "NEW_MSG", "sender": current_user, "content": cipher}
                if target == 'ALL':
                    for u, c in online_clients.items():
                        if u != current_user:
                            try: c.send(json.dumps(fwd_msg).encode())
                            except: pass
                elif target in online_clients:
                    try: online_clients[target].send(json.dumps(fwd_msg).encode())
                    except: pass

            elif action == 'SEARCH':
                trapdoor = data['trapdoor']
                matched_ids = search_index.get(trapdoor, [])
                results = [message_store[mid] for mid in matched_ids]
                conn.send(json.dumps({"status": "OK", "results": results, "type": "SEARCH_RES"}).encode())

            elif action == 'PIR_QUERY':
                q_vec = data['query_vector']
                pub_key = data['pub_key']
                if q_vec:
                    total = q_vec[0]
                    for i in range(1, len(q_vec)):
                        total = SimplePaillier.add(pub_key, total, q_vec[i])
                    conn.send(json.dumps({"status": "OK", "result": total, "type": "PIR_RES"}).encode())

            elif action == 'COMPUTE_SALARY':
                salary_data.append(data['enc_salary'])
                conn.send(json.dumps({"status": "OK", "msg": "薪资已加密上报"}).encode())

            elif action == 'GET_AVG_SALARY':
                if not salary_data:
                    conn.send(json.dumps({"status": "FAIL", "msg": "暂无数据"}).encode())
                else:
                    pub_key = data['pub_key']
                    enc_sum = salary_data[0]
                    for i in range(1, len(salary_data)):
                        enc_sum = SimplePaillier.add(pub_key, enc_sum, salary_data[i])
                    conn.send(json.dumps({"status": "OK", "enc_sum": enc_sum, "count": len(salary_data), "type": "SALARY_RES"}).encode())

    except Exception as e:
        # 核心修改：这里会把报错打印出来！
        print(f"[SERVER ERROR] Error handling client {addr}:")
        traceback.print_exc() 
    finally:
        if current_user and current_user in online_clients:
            del online_clients[current_user]
        conn.close()

def start_server_thread():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(('0.0.0.0', CONFIG['server_port']))
        server.listen()
        print(f"[SERVER] Listening on port {CONFIG['server_port']}")
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
    except OSError:
        print("[SERVER] Port busy, assuming server already running.")