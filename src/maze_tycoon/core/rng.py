import random
from typing import Sequence, TypeVar

T = TypeVar("T")

class RNG:
    def __init__(self, seed: int | None = None):
        self._seed = seed if seed is not None else random.randrange(2**31)
        self._rng = random.Random(self._seed)

    @property
    def seed(self) -> int: return self._seed
    def randint(self, a: int, b: int) -> int: return self._rng.randint(a, b)
    def choice(self, seq: Sequence[T]) -> T: return self._rng.choice(seq)
    def shuffle(self, seq: list[T]) -> None: self._rng.shuffle(seq)
    def random(self) -> float: return self._rng.random()
