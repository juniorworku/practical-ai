"""A missing prediction remains a routing failure, not a dropped row."""
def report(cases, predictions):
    if len({row['id'] for row in cases}) != len(cases):
        raise ValueError('duplicate case')
    labels = {'billing', 'technical'}
    if any(row['gold'] not in labels for row in cases):
        raise ValueError('unknown gold label')
    ids = {row['id'] for row in cases}
    if set(predictions) - ids:
        raise ValueError('prediction without case')
    matrix = {(gold, pred): 0 for gold in labels for pred in labels | {'review'}}
    missing = 0
    for row in cases:
        prediction = predictions.get(row['id'])
        if prediction is None:
            missing += 1
            prediction = 'review'
        if prediction not in labels | {'review'}:
            raise ValueError('unknown prediction')
        matrix[row['gold'], prediction] += 1
    recall = {}
    for label in sorted(labels):
        total = sum(value for (gold, _), value in matrix.items() if gold == label)
        recall[label] = matrix[label, label] / total if total else None
    return {'attempted': len(cases), 'missing': missing, 'recall': recall,
            'correct': sum(matrix[label, label] for label in labels)}

cases = [{'id': 'a', 'gold': 'billing'}, {'id': 'b', 'gold': 'billing'},
         {'id': 'c', 'gold': 'technical'}, {'id': 'd', 'gold': 'technical'}]
result = report(cases, {'a': 'billing', 'b': 'technical', 'c': 'technical'})
assert result == {'attempted': 4, 'missing': 1,
                  'recall': {'billing': .5, 'technical': .5}, 'correct': 2}
print('4 attempted, 2 correct; missing prediction retained; recall .5 for each class')
