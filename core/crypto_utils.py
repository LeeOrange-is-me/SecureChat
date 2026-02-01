import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util import number
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes # <--- 这是一个独立的函数
from Crypto.Hash import SHA256

class AESCipher:
    def __init__(self, key_str):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key_str.encode()).digest()

    def encrypt(self, raw):
        if not isinstance(raw, str):
            raw = str(raw)
        raw = pad(raw.encode(), self.bs)
        
        # --- [修正点 1] ---
        # 以前写错了: iv = number.get_random_bytes(self.bs)
        # 正确写法是直接调用 get_random_bytes:
        iv = get_random_bytes(self.bs) 
        # -----------------
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8')

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:self.bs]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[self.bs:]), self.bs).decode('utf-8')

def hash_password(password, salt=None):
    if not salt:
        # --- [修正点 2] ---
        salt = get_random_bytes(16)
        # -----------------
    
    if isinstance(password, str):
        password = password.encode()
        
    # 确保使用 SHA256 类
    key = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)
    
    return key, salt

def verify_password(stored_key, stored_salt, input_password):
    key, _ = hash_password(input_password, stored_salt)
    return key == stored_key