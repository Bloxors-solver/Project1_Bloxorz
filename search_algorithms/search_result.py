from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node


@dataclass(frozen=True, slots=True)
class SearchResult:
    algorithm: str
    goal_node: Node | None
    actions: tuple[str, ...]

    search_time_ms: float
    peak_memory_mb: float
    expanded_nodes: int
    solution_length: int
    total_cost: float

    @property
    def solved(self) -> bool:
        return self.goal_node is not None

    def as_dict(self) -> dict[str, object]:
        return {
            "algorithm": self.algorithm,
            "solved": self.solved,
            "search_time_ms": round(self.search_time_ms, 4),
            "peak_memory_mb": round(self.peak_memory_mb, 4),
            "expanded_nodes": self.expanded_nodes,
            "solution_length": self.solution_length,
            "total_cost": self.total_cost,
        }