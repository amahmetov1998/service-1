from uuid import UUID


def get_user_cache_key(user_uuid: UUID) -> str:
    return f"user:{user_uuid}"
