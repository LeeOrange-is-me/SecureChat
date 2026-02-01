import random
from Crypto.Util import number

class SimplePaillier:
    def __init__(self):
        self.n = None
        self.g = None
        self.lmb = None
        self.mu = None

    def generate_keys(self, bit_length=128):
        p = number.getPrime(bit_length // 2)
        q = number.getPrime(bit_length // 2)
        self.n = p * q
        self.n_sq = self.n * self.n
        self.g = self.n + 1
        self.lmb = (p - 1) * (q - 1)
        self.mu = number.inverse(self.lmb, self.n)
        return (self.n, self.g), (self.lmb, self.mu)

    @staticmethod
    def encrypt(pub, m):
        n, g = pub
        n_sq = n * n
        r = random.randint(1, n - 1)
        return (pow(g, m, n_sq) * pow(r, n, n_sq)) % n_sq

    @staticmethod
    def decrypt(priv, pub, c):
        lmb, mu = priv
        n, _ = pub
        n_sq = n * n
        x = pow(c, lmb, n_sq)
        L = (x - 1) // n
        return (L * mu) % n

    @staticmethod
    def add(pub, c1, c2):
        n, _ = pub
        n_sq = n * n
        return (c1 * c2) % n_sq