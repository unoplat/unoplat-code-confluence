from __future__ import annotations

from typing import Protocol


class BrowserOpener(Protocol):
    def open(self, url: str) -> bool: ...
