import re

def validate_email(email: str) -> bool:
    """
    Validates the format of an email address using a regex.
    Returns True if valid, False otherwise.
    """
    # This regex checks for a standard email format.
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return True
    return False

def validate_password(password: str) -> list:
    """
    Validates password strength. Returns a list of error messages.
    """
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number.")

    return errors