from typing import Any, Optional

from pydantic import BaseModel


class Attachment(BaseModel):
    buffer: Any
    extension: str
    url: Optional[str]
