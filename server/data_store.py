# 模拟内存数据库
class DataStore:
    def __init__(self):
        self.clients = {}        # {username: socket_conn}
        self.message_store = []  # [{sender, cipher_text, id}, ...]
        self.search_index = {}   # {trapdoor: [msg_id1, msg_id2]}
        self.salary_data = []    # [enc_salary1, enc_salary2]
        # PIR 演示用的“全网用户库”
        self.users_db = ["Alice", "Bob", "Charlie", "David"] 

# 全局单例
db = DataStore()