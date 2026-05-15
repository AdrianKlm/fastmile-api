from __future__ import annotations

import requests


class RouterClient:
    def __init__(self, host: str, timeout: int = 30) -> None:
        self.host = host
        self.timeout = timeout

    def fetch_status_html(self) -> str:
        response = requests.get(
            f"https://{self.host}/status.php",
            timeout=self.timeout,
            verify=False,
        )
        response.raise_for_status()
        return response.text
