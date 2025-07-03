# utils.py
import random
import string

def generate_random_password(length=12):
    """Generates a secure, random password."""
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = '!@#$%^&*()'

    # Ensure at least one of each character type
    password_chars = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]

    # Fill the rest of the password
    all_chars = lowercase + uppercase + digits + special_chars
    password_chars += random.choices(all_chars, k=length - 4)

    random.shuffle(password_chars)
    return ''.join(password_chars)
