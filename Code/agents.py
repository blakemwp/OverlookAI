import numpy as np
from config import (
    PHOTOGRAPHER_DURATION, PHOTOGRAPHER_DURATION_MEAN, PHOTOGRAPHER_DURATION_STD,
    SOCIALIZER_DURATION_MEAN, SOCIALIZER_DURATION_STD,
)

_next_id = 0

def _new_id():
    global _next_id
    _next_id += 1
    return _next_id


class Agent:
    """Base class. Everyone gets a threshold roll and a state machine."""

    def __init__(self, agent_type: str, rng: np.random.Generator):
        self.id = _new_id()
        self.agent_type = agent_type
        self.state = "entering"  # entering | viewing | waiting | departing
        self.slot_index: int | None = None
        self.decision_threshold = rng.random()
        self.ticks_waiting = 0
        self.timer: int | None = None

    def __repr__(self):
        return f"{self.agent_type[0]}{self.id}"


class Photographer(Agent):
    """Camps a slot for 5-15 min. Doesn't care about neighbours."""

    def __init__(self, rng: np.random.Generator):
        super().__init__("Photographer", rng)
        raw = rng.normal(PHOTOGRAPHER_DURATION_MEAN, PHOTOGRAPHER_DURATION_STD)
        self.timer = int(np.clip(round(raw), *PHOTOGRAPHER_DURATION))


class Viewer(Agent):
    """Wants personal space (<=1 neighbour). No fixed timer — leaves when annoyed."""

    def __init__(self, rng: np.random.Generator):
        super().__init__("Viewer", rng)
        self.timer = None


class Socializer(Agent):
    """Seeks the most crowded empty slot. Timer is normally distributed."""

    def __init__(self, rng: np.random.Generator):
        super().__init__("Socializer", rng)
        raw = rng.normal(SOCIALIZER_DURATION_MEAN, SOCIALIZER_DURATION_STD)
        self.timer = max(1, int(round(raw)))
