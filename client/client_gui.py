import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import json
import threading
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

from core.crypto_utils import AESCipher
from core.paillier import SimplePaillier
from core.sse_utils import generate_trapdoor, extract_keywords
from client.secure_db import save_keys, load_keys

with open(os.path.join(root_dir, 'config.json'), 'r') as f:
    CONFIG = json.load(f)

class SecureChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecureChat v2.0 - Encrypted System")
        self.root.geometry("900x650")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.sock = None
        self.username = None
        self.aes = AESCipher(CONFIG['shared_secret'])
        self.paillier = SimplePaillier()
        self.pub_k, self.priv_k = None, None
        self.is_connected = False
        
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.show_login_screen()

    def connect_server(self):
        if self.is_connected: return True
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((CONFIG['server_ip'], CONFIG['server_port']))
            self.is_connected = True
            return True
        except Exception as e:
            messagebox.showerror("连接错误", f"无法连接服务器: {e}")
            return False

    def show_login_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.main_container)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(frame, text="🔐 SecureChat", font=("Helvetica", 24, "bold"), fg="#333").pack(pady=20)
        
        tk.Label(frame, text="用户名:", font=("Arial", 12)).pack(anchor="w")
        self.entry_user = ttk.Entry(frame, width=30)
        self.entry_user.pack(pady=5)
        
        tk.Label(frame, text="密码:", font=("Arial", 12)).pack(anchor="w")
        self.entry_pass = ttk.Entry(frame, show="*", width=30)
        self.entry_pass.pack(pady=5)
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="登录", command=self.do_login).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="注册", command=self.do_register).pack(side=tk.LEFT, padx=10)

    # --- 修复后的注册逻辑 ---
    def do_register(self):
        if not self.connect_server(): return
        
        u, p = self.entry_user.get(), self.entry_pass.get()
        if not u or not p: 
            messagebox.showwarning("提示", "请输入用户名和密码")
            return
        
        try:
            msg = json.dumps({"action": "REGISTER", "username": u, "password": p})
            self.sock.send(msg.encode())
            
            raw = self.sock.recv(1024).decode()
            if not raw:
                # 抛出异常，触发下方的 except
                raise ConnectionError("Server closed connection")
                
            resp = json.loads(raw)
            if resp['status'] == 'OK':
                messagebox.showinfo("注册成功", resp['msg'])
            else:
                messagebox.showerror("注册失败", resp['msg'])
        except Exception as e:
            # 这里使用了 as e，所以 e 是存在的
            print(f"Register Error: {e}")
            messagebox.showerror("错误", f"注册时发生错误: {e}")
            self.is_connected = False
            self.sock.close()

    def do_login(self):
        if not self.connect_server(): return
        u, p = self.entry_user.get(), self.entry_pass.get()
        if not u or not p: return messagebox.showwarning("提示", "请输入用户名和密码")
        
        try:
            self.sock.send(json.dumps({"action": "LOGIN", "username": u, "password": p}).encode())
            raw = self.sock.recv(1024).decode()
            if not raw: raise ConnectionError("Server closed connection")
            
            resp = json.loads(raw)
            if resp['status'] == 'OK':
                self.username = u
                self.pub_k, self.priv_k = load_keys(u)
                if not self.pub_k:
                    self.pub_k, self.priv_k = self.paillier.generate_keys(128)
                    save_keys(u, self.pub_k, self.priv_k)
                
                t = threading.Thread(target=self.recv_loop, daemon=True)
                t.start()
                
                self.show_main_screen()
                self.sock.send(json.dumps({"action": "GET_FRIENDS"}).encode())
            else:
                messagebox.showerror("登录失败", resp['msg'])
                self.sock.close()
                self.is_connected = False
        except Exception as e:
            messagebox.showerror("错误", f"登录出错: {e}")
            self.is_connected = False

    def show_main_screen(self):
        self.clear_screen()
        toolbar = tk.Frame(self.main_container, height=40, bg="#eee")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Button(toolbar, text="➕ 添加好友", command=self.add_friend_ui).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar, text="🔍 云端搜索 (SSE)", command=self.search_ui).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar, text="🕵️ 隐匿查询 (PIR)", command=self.pir_ui).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(toolbar, text="💰 隐私薪资 (MPC)", command=self.salary_ui).pack(side=tk.LEFT, padx=5, pady=5)
        
        paned = tk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_frame = tk.Frame(paned, width=200, bg="white")
        tk.Label(left_frame, text="好友 / 群组", bg="#ddd").pack(fill=tk.X)
        self.friend_list = tk.Listbox(left_frame, font=("Arial", 11))
        self.friend_list.pack(fill=tk.BOTH, expand=True)
        self.friend_list.insert(tk.END, "ALL") 
        self.friend_list.bind('<<ListboxSelect>>', self.on_friend_select)
        paned.add(left_frame)
        
        right_frame = tk.Frame(paned)
        self.chat_display = tk.Text(right_frame, state='disabled', font=("微软雅黑", 10))
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display.tag_config('me', foreground='green', justify='right')
        self.chat_display.tag_config('friend', foreground='blue', justify='left')
        self.chat_display.tag_config('system', foreground='gray', justify='center')

        input_frame = tk.Frame(right_frame, height=50)
        input_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_frame, text="发送给:", fg="gray").pack(side=tk.LEFT)
        self.lbl_target = tk.Label(input_frame, text="ALL", font=("Arial", 10, "bold"), fg="#d9534f")
        self.lbl_target.pack(side=tk.LEFT, padx=5)
        self.entry_msg = ttk.Entry(input_frame)
        self.entry_msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.entry_msg.bind("<Return>", lambda e: self.send_msg())
        ttk.Button(input_frame, text="发送", command=self.send_msg).pack(side=tk.RIGHT)
        paned.add(right_frame)
        
        status_bar = tk.Label(self.main_container, text=f"🟢 已连接 | 当前用户: {self.username}", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def clear_screen(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def log(self, text, tag=None):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, text + "\n", tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def recv_loop(self):
        while True:
            try:
                msg = self.sock.recv(8192).decode('utf-8')
                if not msg: break
                try: data = json.loads(msg)
                except: continue
                
                msg_type = data.get('type')
                if msg_type == 'NEW_MSG':
                    try: content = self.aes.decrypt(data['content'])
                    except: content = "[解密失败]"
                    self.log(f"{data['sender']}: {content}", 'friend')
                elif msg_type == 'MSG_ACK':
                    try: content = self.aes.decrypt(data['content'])
                    except: content = "..."
                    self.log(f"我: {content}", 'me')
                elif msg_type == 'FRIEND_LIST':
                    self.friend_list.delete(0, tk.END)
                    self.friend_list.insert(tk.END, "ALL")
                    for f in data['friends']: self.friend_list.insert(tk.END, f)
                elif msg_type == 'SEARCH_RES':
                    res = f"找到 {len(data['results'])} 条消息:\n"
                    for r in data['results']:
                        try: dec = self.aes.decrypt(r['content'])
                        except: dec = "???"
                        res += f"- {r['sender']}: {dec}\n"
                    messagebox.showinfo("搜索结果", res)
                elif msg_type == 'PIR_RES':
                    val = self.paillier.decrypt(self.priv_k, self.pub_k, data['result'])
                    exists = "✅ 存在" if val >= 1 else "❌ 不存在"
                    messagebox.showinfo("PIR 结果", f"隐匿查询结果: {exists}")
                elif msg_type == 'SALARY_RES':
                    total = self.paillier.decrypt(self.priv_k, self.pub_k, data['enc_sum'])
                    avg = total / data['count']
                    messagebox.showinfo("隐私计算", f"平均薪资: {avg:.2f}")
                elif 'msg' in data:
                    self.log(f"[系统]: {data['msg']}", 'system')
            except Exception as e:
                print("Connection lost", e)
                break

    def send_msg(self):
        txt = self.entry_msg.get()
        if not txt: return
        target = self.lbl_target.cget("text")
        enc = self.aes.encrypt(txt)
        tds = [generate_trapdoor(k) for k in extract_keywords(txt)]
        self.sock.send(json.dumps({"action": "SEND_MSG", "target": target, "cipher_text": enc, "trapdoors": tds}).encode())
        self.entry_msg.delete(0, tk.END)

    def on_friend_select(self, event):
        sel = self.friend_list.curselection()
        if sel: self.lbl_target.config(text=self.friend_list.get(sel[0]))

    def add_friend_ui(self):
        f = simpledialog.askstring("添加", "输入好友名:")
        if f: 
            self.sock.send(json.dumps({"action": "ADD_FRIEND", "friend_name": f}).encode())
            self.root.after(1000, lambda: self.sock.send(json.dumps({"action": "GET_FRIENDS"}).encode()))
            
    def search_ui(self):
        k = simpledialog.askstring("搜索", "关键词:")
        if k: self.sock.send(json.dumps({"action": "SEARCH", "trapdoor": generate_trapdoor(k)}).encode())
        
    def pir_ui(self):
        t = simpledialog.askstring("PIR", "查询用户:")
        if t:
            vec = [self.paillier.encrypt(self.pub_k, 1 if u == t else 0) for u in ["Alice", "Bob", "Charlie", "David"]]
            self.sock.send(json.dumps({"action": "PIR_QUERY", "query_vector": vec, "pub_key": self.pub_k}).encode())
            
    def salary_ui(self):
        s = simpledialog.askinteger("薪资", "金额:")
        if s: self.sock.send(json.dumps({"action": "COMPUTE_SALARY", "enc_salary": self.paillier.encrypt(self.pub_k, s)}).encode())
        if messagebox.askyesno("计算", "计算平均值?"): self.sock.send(json.dumps({"action": "GET_AVG_SALARY", "pub_key": self.pub_k}).encode())

def start_client_gui():
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))
    app = SecureChatApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_client_gui()