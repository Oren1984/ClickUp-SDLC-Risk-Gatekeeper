from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Generator


@contextmanager
def timer() -> Generator[dict, None, None]:
    """
    Context manager that measures wall-clock elapsed time in seconds.

    Usage:
        with timer() as t:
            do_work()
        elapsed = t["elapsed"]  # float, seconds

    The result dict is populated on exit even if an exception is raised.
    """
    result: dict = {"elapsed": 0.0}
    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start
