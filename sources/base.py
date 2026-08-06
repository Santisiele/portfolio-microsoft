from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Source:
    origin: str
    fetch: Callable[[], list]
    steps: list = field(default_factory=list)
    origin_column: str = "Origen"

    def load(self):
        rows = self.fetch()
        for row in rows:
            row[self.origin_column] = self.origin
        for step in self.steps:
            rows = step(rows)
        return rows


def load_module(sources):
    rows = []
    for source in sources:
        rows += source.load()
    return rows