"""Independent verifier. Standard library only; imports no b04-lfv code.

Generate connected simple max-degree-three graphs by vertex augmentation and
exact pairwise isomorphism rejection; exhaust all LFV choices without a horizon.
"""
import argparse
import functools
import itertools
import json
import resource
import time
from collections import Counter, defaultdict
from pathlib import Path


def colors(g):
    c = tuple(x.bit_count() for x in g)
    for _ in g:
        profiles = [(c[i], tuple(sorted(c[j] for j in range(len(g)) if g[i] >> j & 1)))
                    for i in range(len(g))]
        ids = {x: i for i, x in enumerate(sorted(set(profiles)))}
        new = tuple(ids[x] for x in profiles)
        if new == c:
            break
        c = new
    signature = tuple(sorted((c[i], tuple(sorted(c[j] for j in range(len(g))
                                               if g[i] >> j & 1)))
                             for i in range(len(g))))
    return c, signature


def isomorphic(a, ca, b, cb):
    n = len(a)
    mapping = {}
    used = set()

    def search():
        if len(mapping) == n:
            return True
        best = None
        for u in range(n):
            if u in mapping:
                continue
            candidates = [v for v in range(n) if v not in used and ca[u] == cb[v]
                          and all(((a[u] >> x) & 1) == ((b[v] >> y) & 1)
                                  for x, y in mapping.items())]
            if not candidates:
                return False
            if best is None or len(candidates) < len(best[1]):
                best = u, candidates
        u, candidates = best
        for v in candidates:
            mapping[u] = v
            used.add(v)
            if search():
                return True
            used.remove(v)
            del mapping[u]
        return False
    return search()


def extend(previous):
    buckets = defaultdict(list)
    for g in previous:
        n = len(g)
        available = [v for v in range(n) if g[v].bit_count() < 3]
        for k in range(1, min(3, len(available)) + 1):
            for neighbors in itertools.combinations(available, k):
                h = list(g) + [sum(1 << v for v in neighbors)]
                for v in neighbors:
                    h[v] |= 1 << n
                h = tuple(h)
                c, sig = colors(h)
                if not any(isomorphic(h, c, old, oldc) for old, oldc in buckets[sig]):
                    buckets[sig].append((h, c))
    return [g for bucket in buckets.values() for g, _ in bucket]


def word(g):
    return ''.join(str((g[i] >> j) & 1) for i in range(len(g))
                   for j in range(i + 1, len(g)))


def exact(g):
    n = len(g)
    if n == 1:
        return 0, 0, 0
    adj = [tuple(j for j in range(n) if g[i] >> j & 1) for i in range(n)]

    @functools.lru_cache(None)
    def search(x, c):
        if all(c):
            return 0, 0
        largest_time, largest_frequency = 0, max(c)
        minimum = min(c[y] for y in adj[x])
        for y in adj[x]:
            if c[y] != minimum:
                continue
            cc = list(c)
            cc[y] += 1
            future_time, future_frequency = search(y, tuple(cc))
            largest_time = max(largest_time, 1 + future_time)
            largest_frequency = max(largest_frequency, future_frequency)
        return largest_time, largest_frequency

    answers = [search(x, tuple(int(v == x) for v in range(n))) for x in range(n)]
    return max(t for t, _ in answers), max(m for _, m in answers), search.cache_info().currsize


def witness(path):
    data = json.loads(path.read_text())
    n, bits, trajectory = data['n'], iter(data['word']), data['path']
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if next(bits) == '1':
                adj[i].add(j)
                adj[j].add(i)
    assert trajectory[0] == data['root']
    c = [0] * n
    first = [None] * n
    c[trajectory[0]] = 1
    first[trajectory[0]] = 0
    before_max, cover = 1, None
    for t, (x, y) in enumerate(zip(trajectory, trajectory[1:]), 1):
        assert cover is None, 'trajectory continues after first coverage'
        assert y in adj[x], (t, 'not an edge')
        assert c[y] == min(c[z] for z in adj[x]), (t, 'not a minimum')
        c[y] += 1
        if first[y] is None:
            first[y] = t
        if all(c):
            cover = t
        else:
            before_max = max(before_max, max(c))
    assert cover is not None
    observed = cover if data['objective'] == 'time' else before_max
    assert observed == data['value']
    return dict(file=str(path), legal=True, T=cover, M=before_max,
                degrees=sorted(map(len, adj)), counters=c,
                first_hits=first, sum_first_hits=sum(first))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-n', type=int, default=9)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (1500, 1500))
    start = time.monotonic()
    graphs = [(0,)]
    rows = []
    records = []
    for n in range(1, args.max_n + 1):
        if n > 1:
            graphs = extend(graphs)
        row = dict(n=n, classes=len(graphs), T=0, M=0, tree_T=0,
                   cubic_classes=0, cubic_T=None, states=0)
        for g in graphs:
            t, m, states = exact(g)
            row['states'] += states
            if t >= row['T']:
                row['T'], row['time_graph'] = t, word(g)
            if m >= row['M']:
                row['M'], row['frequency_graph'] = m, word(g)
            if sum(x.bit_count() for x in g) == 2 * (n - 1):
                row['tree_T'] = max(row['tree_T'], t)
            if all(x.bit_count() == 3 for x in g):
                row['cubic_classes'] += 1
                row['cubic_T'] = max(row['cubic_T'] or 0, t)
            records.append(dict(n=n, word=word(g), T=t, M=m, states=states))
        row['elapsed_seconds'] = time.monotonic() - start
        rows.append(row)
        print(json.dumps(row), flush=True)
    with open('independent_graph_results.jsonl', 'w') as f:
        for record in records:
            f.write(json.dumps(record) + '\n')
    witnesses = [witness(Path('../data/exact') / name)
                 for name in ('witness_n12.json', 'frequency_n12.json')]
    result = dict(rows=rows, witnesses=witnesses,
                  cpu_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime)
    Path('independent_results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(witnesses=witnesses)), flush=True)


if __name__ == '__main__':
    main()
