"""Generator for synthetic delivery order records."""

import random
import time
from dataclasses import dataclass


@dataclass
class Order:
    order_id: int
    priority: int          # 1-5, creates heavy duplicates for that sort key
    deadline: float        # Unix timestamp - mostly unique floats
    distance_km: float
    parcel_weight: float
    zone_id: int           # 1-20, used for integer-key (radix/counting) sort


def generate_orders(
    n: int,
    seed: int,
    structure: str = "random",
) -> list[Order]:
    """Generate n synthetic delivery orders.

    Parameters
    ----------
    n:
        Number of records to generate.
    seed:
        Random seed for reproducibility.
    structure:
        One of: 'random', 'sorted_deadline', 'reverse_deadline',
        'many_duplicates_priority', 'nearly_sorted_deadline'.
    """
    rng = random.Random(seed)
    base_time = 1_700_000_000.0  # a fixed past timestamp

    orders = []
    for i in range(n):
        order = Order(
            order_id=i,
            priority=rng.randint(1, 5),
            deadline=base_time + rng.uniform(0, 86_400 * 7),
            distance_km=round(rng.uniform(0.5, 50.0), 2),
            parcel_weight=round(rng.uniform(0.1, 30.0), 2),
            zone_id=rng.randint(1, 20),
        )
        orders.append(order)

    if structure in ("random", "composite", "integer_zone"):
        pass

    elif structure == "sorted":
        orders.sort(key=lambda o: o.deadline)

    elif structure == "reverse_sorted":
        orders.sort(key=lambda o: o.deadline, reverse=True)

    elif structure == "many_duplicates":
        # sort by priority so there are only 5 distinct key values
        orders.sort(key=lambda o: o.priority)
        groups: dict[int, list] = {}
        for o in orders:
            groups.setdefault(o.priority, []).append(o)
        for grp in groups.values():
            rng.shuffle(grp)
        result = []
        for p in sorted(groups):
            result.extend(groups[p])
        orders = result

    elif structure == "nearly_sorted":
        orders.sort(key=lambda o: o.deadline)
        # apply about 2% random swaps
        num_swaps = max(1, n // 50)
        for _ in range(num_swaps):
            i, j = rng.randrange(n), rng.randrange(n)
            orders[i], orders[j] = orders[j], orders[i]

    else:
        raise ValueError(f"Unknown structure: {structure!r}")

    return orders


def deadline_key(o: Order) -> float:
    return o.deadline


def priority_key(o: Order) -> int:
    return o.priority


def composite_key(o: Order) -> tuple[int, float]:
    return (o.priority, o.deadline)


def zone_key(o: Order) -> int:
    """Integer key suitable for radix sort."""
    return o.zone_id


SORT_KEYS = {
    "deadline": deadline_key,
    "priority": priority_key,
    "composite": composite_key,
    "zone_id": zone_key,
}

STRUCTURES = [
    "random",
    "sorted",
    "reverse_sorted",
    "nearly_sorted",
    "many_duplicates",
    "composite",
    "integer_zone",
]

STRUCTURE_KEY_MAP = {
    "random": ("deadline", deadline_key),
    "sorted": ("deadline", deadline_key),
    "reverse_sorted": ("deadline", deadline_key),
    "nearly_sorted": ("deadline", deadline_key),
    "many_duplicates": ("priority", priority_key),
    "composite": ("composite", composite_key),
    "integer_zone": ("zone_id", zone_key),
}
