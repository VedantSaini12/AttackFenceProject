import re

ALLOWED_DOMAINS = ["evaluationportal.in", "example.com"]

def validate_email(email: str) -> bool:
    """
    Validates the format of an email address using a regex and checks if the domain is allowed.
    Returns True if valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+)\.[a-zA-Z]{2,}$"
    match = re.match(pattern, email)
    if match:
        domain = email.split('@')[1].lower()
        if domain in ALLOWED_DOMAINS:
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

def validate_name(name: str) -> bool:
    """
    Validates that a name contains only letters and spaces,
    and is not empty or just whitespace.
    """
    name = name.strip()
    if not name:
        return False
        
    # Check that all characters are either letters or spaces
    return all(c.isalpha() or c.isspace() for c in name)