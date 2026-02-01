import hashlib

def generate_trapdoor(keyword):
    return hashlib.sha256(keyword.encode()).hexdigest()

def extract_keywords(text):
    return text.split()