from collections import deque
import numpy as np

from Code.agents import Agent
from config import NUM_SLOTS, DEAD_ZONE_NEIGHBOR_MIN, DEAD_ZONE_DENSITY_TICKS


class Overlook:
    """1D railing of NUM_SLOTS + an overflow waiting area."""

    def __init__(self, rng: np.random.Generator):
        self.rng = rng
        self.slots: list[Agent | None] = [None] * NUM_SLOTS
        self.waiting_area: deque[Agent] = deque()
        self.dead_zones: set[int] = set()
        self._crowd_streak: list[int] = [0] * NUM_SLOTS  # for dead-zone tracking

    # -- read-only helpers --

    def empty_indices(self) -> list[int]:
        return [i for i, s in enumerate(self.slots) if s is None]

    def occupied_count(self) -> int:
        return sum(1 for s in self.slots if s is not None)

    def neighbor_count(self, idx: int) -> int:
        """How many of the left/right neighbours are occupied."""
        count = 0
        if idx > 0 and self.slots[idx - 1] is not None:
            count += 1
        if idx < NUM_SLOTS - 1 and self.slots[idx + 1] is not None:
            count += 1
        return count

    def _pick(self, candidates: list[int]) -> int | None:
        """Random tie-breaker over a candidate slot list (or None if empty)."""
        if not candidates:
            return None
        return int(self.rng.choice(candidates))

    def best_slot_for_viewer(self) -> int | None:
        """Random empty slot with <=1 neighbour, ignoring dead zones."""
        candidates = [
            i for i in self.empty_indices()
            if i not in self.dead_zones and self.neighbor_count(i) <= 1
        ]
        return self._pick(candidates)

    def best_slot_for_socializer(self) -> int | None:
        """Random empty slot among those tied for the most neighbours."""
        empties = self.empty_indices()
        if not empties:
            return None
        max_n = max(self.neighbor_count(i) for i in empties)
        candidates = [i for i in empties if self.neighbor_count(i) == max_n]
        return self._pick(candidates)

    def any_empty_slot(self) -> int | None:
        return self._pick(self.empty_indices())

    # -- mutations --

    def place_agent(self, agent: Agent, idx: int):
        assert self.slots[idx] is None
        self.slots[idx] = agent
        agent.slot_index = idx
        agent.state = "viewing"

    def remove_agent(self, agent: Agent):
        if agent.slot_index is not None:
            self.slots[agent.slot_index] = None
            agent.slot_index = None
        agent.state = "departing"

    def add_to_waiting(self, agent: Agent):
        agent.state = "waiting"
        agent.ticks_waiting = 0
        self.waiting_area.append(agent)

    def update_dead_zones(self):
        """If a slot stays crowded long enough, viewers give up on it forever."""
        for i in range(NUM_SLOTS):
            if self.slots[i] is not None and self.neighbor_count(i) >= DEAD_ZONE_NEIGHBOR_MIN:
                self._crowd_streak[i] += 1
            else:
                self._crowd_streak[i] = 0
            if self._crowd_streak[i] >= DEAD_ZONE_DENSITY_TICKS:
                self.dead_zones.add(i)
