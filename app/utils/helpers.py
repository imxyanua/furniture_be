import uuid


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}{unique_id}" if prefix else unique_id
