import statistics
from math import trunc
from numbers import Number

from logger import log


def is_null_or_whitespace(value: str):
    return value is None or value.strip() == ""

def try_or(func, default=None, exc=Exception):
    try: return func()
    except exc as e:
        log(f"Failed to fetch value for {func}. Returning default {default}\nException: {e}")
        return default

def avg(values: list[float]):
    return sum(values) / len(values) if values else 0

def med(values: list[float]):
    return statistics.median(values) if values else 0

def sec_to_mmss(seconds: float):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{seconds:05.2f}"


