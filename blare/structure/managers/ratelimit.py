from typing import Any, Dict, Optional
from discord.ext.commands import CooldownMapping

# robbed :3
mappings: Dict[str, CooldownMapping] = {}


def handle_bucket(key: Any) -> Any:
    return key


def ratelimiter(
    bucket: str,
    key: Any,
    rate: int,
    per: float
) -> Optional[int]:
    if not (mapping := mappings.get(bucket)):

        mapping = mappings[bucket] = CooldownMapping.from_cooldown(
            rate, 
            per, 
            handle_bucket
        )

    bucket = mapping.get_bucket(key)
    return bucket.update_rate_limit()