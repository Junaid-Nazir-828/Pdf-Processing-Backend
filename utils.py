import random
import string

def generate_random_string(length=8):
    """Generate a random string for folder naming"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))