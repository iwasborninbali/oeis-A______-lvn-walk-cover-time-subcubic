"""Independent LFV certificates/exclusion checker, Python standard library only.

Does not import the graph generator, pilot, or C++ search. Upper bounds use
forward reachable-state layers, not the producer's backwards memoised DP.
Catalogue completeness uses explicit graph-isomorphism backtracking, not the
producer's individualisation canonical form. See result.md for the arguments.
"""
import argparse
import itertools
import json
from pathlib import Path
import shutil
import time
from fractions import Fraction


def graph(word, n):
    assert len(word) == n*(n-1)//2 and set(word) <= {'0', '1'}
    a = [set() for _ in range(n)]
    p = 0
    for i in range(n):
        for j in range(i+1, n):
            if word[p] == '1':
                a[i].add(j); a[j].add(i)
            p += 1
    assert all(len(x) <= 3 for x in a)
    seen, stack = {0}, [0]
    while stack:
        for w in a[stack.pop()]:
            if w not in seen:
                seen.add(w); stack.append(w)
    assert len(seen) == n
    return tuple(tuple(sorted(x)) for x in a)


def colours(a):
    """Equitable colours and an isomorphism invariant; no canonical labelling."""
    c = tuple(map(len, a))
    while True:
        sig = tuple((c[v], tuple(sorted(c[w] for w in a[v]))) for v in range(len(a)))
        names = {s: i for i, s in enumerate(sorted(set(sig)))}
        d = tuple(names[s] for s in sig)
        if len(set(d)) == len(set(c)):
            # The multiset of final signatures gives more than a colour count.
            return d, tuple(sorted(sig))
        c = d


def isomorphic(a, b, ca, cb):
    if len(a) != len(b):
        return False
    n = len(a)
    mapping = {}
    used = set()
    a_sets = tuple(map(set, a)); b_sets = tuple(map(set, b))
    candidates = [tuple(w for w in range(n) if cb[w] == ca[v]) for v in range(n)]

    def extend():
        if len(mapping) == n:
            return True
        v = min((v for v in range(n) if v not in mapping),
                key=lambda v: (-sum(u in mapping for u in a[v]),
                               sum(w not in used for w in candidates[v])))
        for w in candidates[v]:
            if w in used:
                continue
            if any((u in a_sets[v]) != (x in b_sets[w]) for u, x in mapping.items()):
                continue
            mapping[v] = w; used.add(w)
            if extend():
                return True
            used.remove(w); del mapping[v]
        return False
    return extend()


def catalogues(max_n, directory):
    previous = None
    for n in range(1, max_n+1):
        begun = time.monotonic()
        words = (directory / f'n{n}.txt').read_text().splitlines()
        assert words and len(words) == len(set(words))
        buckets, data = {}, []
        for word in words:
            a = graph(word, n); c, invariant = colours(a)
            bucket = buckets.setdefault(invariant, [])
            assert not any(isomorphic(a, b, c, cb) for b, cb in bucket), ('duplicate', n, word)
            bucket.append((a, c)); data.append(a)
        assert (n != 1) or words == ['']
        attempts = 0
        if previous is not None:
            for a in previous:
                eligible = [v for v in range(n-1) if len(a[v]) < 3]
                for k in range(1, min(3, len(eligible))+1):
                    for links in itertools.combinations(eligible, k):
                        b = tuple(tuple(sorted(a[v] + ((n-1,) if v in links else ())))
                                  for v in range(n-1)) + (links,)
                        cb, invariant = colours(b)
                        assert any(isomorphic(b, x, cb, cx)
                                   for x, cx in buckets.get(invariant, ())), ('missing extension', n, b)
                        attempts += 1
        print(json.dumps(dict(check='catalogue', n=n, graphs=len(words),
                              extensions=attempts, seconds=time.monotonic()-begun)), flush=True)
        previous = data


def replay(filename):
    o = json.loads(filename.read_text())
    n, path = o['n'], o['path']
    a = graph(o['word'], n)
    assert path and path[0] == o['root'] and all(type(v) is int and 0 <= v < n for v in path)
    counts, hits = [0]*n, [None]*n
    counts[path[0]] = 1; hits[path[0]] = 0
    peak = 0
    for t, (v, w) in enumerate(zip(path, path[1:])):
        assert 0 in counts, ('continued after coverage', filename, t)
        peak = max(peak, max(counts))
        assert w in a[v] and counts[w] == min(counts[u] for u in a[v]), ('illegal move', filename, t)
        counts[w] += 1
        if hits[w] is None:
            hits[w] = t+1
    assert min(counts) > 0
    measured = len(path)-1 if o['objective'] == 'time' else peak
    assert measured == o['value'], (filename, measured, o['value'])
    return dict(file=str(filename), first_cover=len(path)-1, max_frequency_before_cover=peak,
                average_first_hit=str(Fraction(sum(hits), n)), final_counts=counts)


def forward_tuple(a):
    """All starts and all adversarial tie choices; stop each path at coverage."""
    n = len(a)
    if n == 1:
        return 0, 0, 0, 1
    layer = {(root, tuple(int(v == root) for v in range(n))) for root in range(n)}
    t = 0; last_terminal = -1; peak = 1; states = 0; largest_layer = 0
    # Proven coarse bound, independently derived in result.md. No truncation
    # is allowed: reaching it is a checker failure, not an upper certificate.
    horizon = 2*n*(3**(n-1)-1) + 1
    while layer:
        assert t <= horizon
        states += len(layer); largest_layer = max(largest_layer, len(layer))
        following = set()
        for v, c in layer:
            least = min(c[w] for w in a[v])
            final_zero = least == 0 and c.count(0) == 1
            for w in a[v]:
                if c[w] != least:
                    continue
                if final_zero:
                    last_terminal = t+1
                    continue
                updated = c[:w] + (c[w]+1,) + c[w+1:]
                peak = max(peak, c[w]+1)
                following.add((w, updated))
        layer = following; t += 1
    assert last_terminal >= 0
    return last_terminal, peak, states, largest_layer


def forward(a):
    """Same forward semantics, represented as Python integers for scale.

    Low four bits: position. Next n bits: visited set. Higher fields: counts.
    Count width follows a proved universal bound, not the producer's 8-bit
    assumption. The explicitly visited set is redundant but saves scans.
    """
    n = len(a)
    if n == 1:
        return 0, 0, 0, 1
    assert n <= 15
    horizon = 2*n*(3**(n-1)-1) + 1
    width = horizon.bit_length()
    count_mask = (1 << width)-1
    offsets = [n+4+v*width for v in range(n)]
    units = [1 << p for p in offsets]
    marked = [1 << (v+4) for v in range(n)]
    full = ((1 << n)-1) << 4
    prepared = [tuple((w, offsets[w], units[w], marked[w]) for w in a[v]) for v in range(n)]
    layer = {root | marked[root] | units[root] for root in range(n)}
    t = 0; last_terminal = -1; peak = 1; states = 0; largest_layer = 0
    while layer:
        assert t <= horizon
        states += len(layer); largest_layer = max(largest_layer, len(layer))
        following = set(); add = following.add
        for state in layer:
            neighbors = prepared[state & 15]
            least = min((state >> offset) & count_mask for _, offset, _, _ in neighbors)
            for w, offset, unit, bit in neighbors:
                if ((state >> offset) & count_mask) != least:
                    continue
                # Replace position, increment destination, mark it visited.
                successor = ((state & -16) + unit) | bit | w
                if successor & full == full:
                    last_terminal = t+1
                    continue
                if least+1 > peak:
                    peak = least+1
                assert least+1 <= horizon
                add(successor)
        layer = following; t += 1
    assert last_terminal >= 0
    return last_terminal, peak, states, largest_layer


def exclusions(min_n, max_n, directory, results, reference=False):
    for n in range(min_n, max_n+1):
        begun = time.monotonic(); total = 0; biggest = 0; worst = 0; freq = 0
        words = (directory / f'n{n}.txt').read_text().splitlines()
        with (results / f'n{n}.jsonl').open() as stream:
            for index, word in enumerate(words):
                row = json.loads(next(stream))
                assert row['word'] == word
                search_layers = forward_tuple if reference else forward
                bound, f, size, width = search_layers(graph(word, n))
                assert bound == max(row['times']), (n, index, 'time', bound, row)
                assert f == max(row['frequencies']), (n, index, 'frequency', f, row)
                assert size == row['states'] or n == 1, (n, index, 'states', size, row['states'])
                total += size; biggest = max(biggest, width)
                worst = max(worst, bound); freq = max(freq, f)
                if (index+1) % 1000 == 0:
                    assert shutil.disk_usage(directory).free > 3*1024**3
                    print(json.dumps(dict(check='checkpoint', n=n, graphs_done=index+1,
                                          states=total, seconds=time.monotonic()-begun)), flush=True)
            assert not stream.read().strip()
        print(json.dumps(dict(check='exclusion', n=n, graphs=len(words),
                              states=total, largest_layer=biggest, worst_time=worst,
                              worst_frequency=freq, seconds=time.monotonic()-begun)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-n', type=int, default=10)
    parser.add_argument('--min-n', type=int, default=1)
    parser.add_argument('--catalog', type=Path, default=Path('catalog'))
    parser.add_argument('--results', type=Path, default=Path('exact'))
    parser.add_argument('--mode', choices=['all', 'catalogues', 'exclusions', 'witnesses'], default='all')
    parser.add_argument('--reference', action='store_true', help='use readable tuple states instead of packed Python integers')
    args = parser.parse_args()
    if args.mode in ('all', 'catalogues'):
        catalogues(args.max_n, args.catalog)
    if args.mode in ('all', 'exclusions'):
        exclusions(args.min_n, args.max_n, args.catalog, args.results, args.reference)
    if args.mode in ('all', 'witnesses'):
        for n in range(args.min_n, args.max_n+1):
            for prefix in ('witness', 'frequency'):
                print(json.dumps(replay(args.results / f'{prefix}_n{n}.json')), flush=True)


if __name__ == '__main__':
    main()
