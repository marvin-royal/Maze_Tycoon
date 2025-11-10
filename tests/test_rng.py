# tests/test_rng.py
from maze_tycoon.core.rng import RNG

def test_rng_reproducible_same_seed():
    a, b = RNG(123), RNG(123)
    assert [a.randint(0, 9) for _ in range(5)] == [b.randint(0, 9) for _ in range(5)]

def test_rng_basic_ops_and_seed_property():
    r = RNG(999)
    assert isinstance(r.seed, int)
    _ = r.random()
    data = list(range(10))
    r.shuffle(data)
    assert sorted(data) == list(range(10))
    # choice / randint smoke
    _ = r.choice(data)
    _ = r.randint(5, 7)
