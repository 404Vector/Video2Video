import uuid


def create_uuid() -> str:
    return str(uuid.uuid1())


__all__ = [
    create_uuid.__name__,
]
