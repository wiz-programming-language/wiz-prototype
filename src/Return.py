from typing import Any

class Return_(RuntimeError):
    def __init__(self, value: Any) -> None:
        self.value = value
