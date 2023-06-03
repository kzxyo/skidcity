from typing import Optional
from typing_extensions import Self
import time

class Cooldown:
    def __init__(self, rate: int, per: float):
        self.rate = rate
        self.per = per
        self._window = 0.0
        self._tokens = self.rate
        self._last = 0.0


    def __repr__(self) -> str:
        return f'<Cooldown rate: {self.rate} per: {self.per} window: {self._window} tokens: {self._tokens}>'


    def get_tokens(self, current: Optional[float] = None) -> int:

        if not current:
            current = time.time()

        tokens = max(self._tokens, 0)

        if current > self._window + self.per:
            tokens = self.rate
        return tokens


    def get_retry_after(self, current: Optional[float] = None) -> float:
        
        current = current or time.time()
        tokens = self.get_tokens(current)

        if tokens == 0:
            return self.per - (current - self._window)

        return 0.0


    def update_rate_limit(self, current: Optional[float] = None, *, tokens: int = 1) -> Optional[float]:

        current = current or time.time()
        self._last = current

        self._tokens = self.get_tokens(current)

        if self._tokens == self.rate:
            self._window = current

        self._tokens -= tokens

        if self._tokens < 0:
            return self.per - (current - self._window)


    def reset(self) -> None:
        self._tokens = self.rate
        self._last = 0.0


    def copy(self) -> Self:
        return Cooldown(self.rate, self.per)


class CooldownMapping:
    def __init__(self, original: Optional[Cooldown]):
        self._cache: Dict[Any, Cooldown] = {}
        self._cooldown: Optional[Cooldown] = original


    def copy(self) -> Self:
        ret = CooldownMapping(self._cooldown, self._type)
        ret._cache = self._cache.copy()
        return ret


    @property
    def valid(self) -> bool:
        return self._cooldown is not None


    @classmethod
    def from_cooldown(cls, rate: float, per: float) -> Self:
        return cls(Cooldown(rate, per))


    def _verify_cache_integrity(self, current: Optional[float] = None) -> None:

        current = current or time.time()
        dead_keys = [k for k, v in self._cache.items() if current > v._last + v.per]
        for k in dead_keys:
            del self._cache[k]

    def create_bucket(self, key: str) -> Cooldown:
        return self._cooldown.copy()  # type: ignore


    def get_bucket(self, key: str, current: Optional[float] = None) -> Optional[Cooldown]:

        self._verify_cache_integrity(current)
        if key not in self._cache:
            bucket = self.create_bucket(key)
            if bucket is not None:
                self._cache[key] = bucket
        else:
            bucket = self._cache[key]

        return bucket

    def update_rate_limit(self, key: str, current: Optional[float] = None, tokens: int = 1) -> Optional[float]:
        bucket = self.get_bucket(message, current)
        if bucket is None:
            return None
        return bucket.update_rate_limit(current, tokens=tokens)