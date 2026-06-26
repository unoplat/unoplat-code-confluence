from __future__ import annotations

import webbrowser


class WebbrowserOpener:
    def open(self, url: str) -> bool:
        return webbrowser.open(url)
