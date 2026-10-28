from logger import log


def is_null_or_whitespace(value: str):
    return value is None or value.strip() == ""

def try_or(func, default=None, exc=Exception):
    try: return func()
    except exc as e:
        log(f"Failed to fetch value for {func}. Returning default {default}\nException: {e}")
        return default