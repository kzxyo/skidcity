import threading
import time
from datetime import datetime
from typing import Optional, Union

from ._hashids import Hashids

_hashids = Hashids()
_ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
_tuuid_lock = threading.Lock()


def from_datetime(datetime: datetime) -> str:
    """Generate tuuid from datetime
    Args:
        datetime (datetime)
    Returns:
        str
    """
    return _hashids.decode(int(datetime.timestamp()))


def from_ts(timestamp: float | int) -> str:
    """Generate tuuid from timestamp
    Args:
        timestamp float | int
    Returns:
        str
    """

    return _hashids.decode(int(timestamp))


def tuuid() -> str:
    """Generate a timstamp based hashid.
    Utilizes a mutex to ensure hashes are unique.
    Returns:
        str: the tuuid
    """
    with _tuuid_lock:
        return _hashids.encode(time.time_ns())


def random() -> str:
    """Generate a timstamp based hashid.
    Utilizes a mutex to ensure hashes are unique.
    Returns:
        str: the tuuid
    """
    with _tuuid_lock:
        return _hashids.encode(time.time_ns())


def decode(tuuid: str, return_type: Optional[str] = "date") -> datetime | int:
    """Decode a tuuid to Timestamp or datetime.dateimte
    Args:
        tuuid (str): A tuuid generated from tuuid.random()
        return_type (Optional[str], optional): Return type. Options  of 'date' or 'ts'. Defaults to "date".
    Returns:
        datetime | int: Decoded hashid
    """

    hashid_decoded = _hashids.decode(tuuid)[0]
    times = hashid_decoded / 1000000000

    timestamp = int(times)
    if return_type == "date":
        return datetime.fromtimestamp(timestamp)

    if return_type in ("ts", "timestamp"):
        return timestamp
