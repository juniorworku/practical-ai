"""All attempted work is charged; unmeasured costs stay unknown."""
from decimal import Decimal
from math import ceil

def summarize(rows):
    if not rows or len({row['id'] for row in rows}) != len(rows):
        raise ValueError('nonempty unique observations required')
    for row in rows:
        if type(row['accepted']) is not bool:
            raise ValueError('acceptance must be a reviewed boolean')
        if type(row['elapsed_ms']) not in (int, float) or not 0 <= row['elapsed_ms'] < float('inf'):
            raise ValueError('finite elapsed time required, including failures')
        cost = row['cost_usd']
        if cost is not None and (not isinstance(cost, Decimal) or not cost.is_finite() or cost < 0):
            raise ValueError('cost must be nonnegative Decimal or unknown')
    times = sorted(row['elapsed_ms'] for row in rows)
    accepted = sum(row['accepted'] for row in rows)
    unknown = sum(row['cost_usd'] is None for row in rows)
    known_cost = sum((row['cost_usd'] for row in rows if row['cost_usd'] is not None), Decimal(0))
    return {'attempted': len(rows), 'accepted': accepted, 'unknown_cost_rows': unknown,
            'p95_all_attempts_ms': times[ceil(.95 * len(times)) - 1],
            'known_cost_usd': known_cost,
            'cost_per_accepted_usd': known_cost / accepted if accepted and not unknown else None}

rows = [{'id': 'ok', 'accepted': True, 'elapsed_ms': 20, 'cost_usd': Decimal('.01')},
        {'id': 'retry_then_fail', 'accepted': False, 'elapsed_ms': 900, 'cost_usd': Decimal('.03')}]
assert summarize(rows)['cost_per_accepted_usd'] == Decimal('.04')
assert summarize(rows)['p95_all_attempts_ms'] == 900
assert summarize([{**rows[0], 'cost_usd': None}])['cost_per_accepted_usd'] is None
print('all work: USD .04 per accepted result; p95 900ms; missing cost stays unknown')
