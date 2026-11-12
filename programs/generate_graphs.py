"""Connected simple subcubic graphs by connected vertex augmentation.

No external packages or catalogues. Isomorphs have an identical canonical
adjacency word, obtained by exhaustive individualisation/refinement.
"""
import argparse, itertools, json, time
from pathlib import Path


def canonical(adj, root=None):
    n = len(adj)
    cells = []
    if root is not None:
        cells.append((root,))
    by_degree = {}
    for v in range(n):
        if v != root:
            by_degree.setdefault(adj[v].bit_count(), []).append(v)
    cells += [tuple(by_degree[d]) for d in sorted(by_degree)]

    def refine(part):
        while True:
            masks = [sum(1 << v for v in cell) for cell in part]
            finer = []
            for cell in part:
                buckets = {}
                for v in cell:
                    sig = tuple((adj[v] & m).bit_count() for m in masks)
                    buckets.setdefault(sig, []).append(v)
                finer.extend(tuple(buckets[sig]) for sig in sorted(buckets))
            if len(finer) == len(part):
                return finer
            part = finer

    def visit(part):
        part = refine(part)
        ambiguous = [(len(c), i) for i, c in enumerate(part) if len(c) > 1]
        if not ambiguous:
            order = [c[0] for c in part]
            return ''.join('1' if adj[order[i]] >> order[j] & 1 else '0'
                           for i in range(n) for j in range(i + 1, n))
        _, i = min(ambiguous)
        return min(visit(part[:i] + [(v,), tuple(w for w in part[i] if w != v)] + part[i+1:])
                   for v in part[i])
    return visit(cells)


def decode(word, n):
    adj = [0] * n
    p = 0
    for i in range(n):
        for j in range(i+1, n):
            if word[p] == '1':
                adj[i] |= 1 << j; adj[j] |= 1 << i
            p += 1
    return adj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-n', type=int, default=8)
    ap.add_argument('--out', default='catalog')
    args = ap.parse_args()
    folder = Path(args.out); folder.mkdir(exist_ok=True)
    words = {''}
    for n in range(1, args.max_n + 1):
        start = time.monotonic()
        attempts = 0
        if n > 1:
            newer = set()
            for word in words:
                adj = decode(word, n-1)
                available = [v for v in range(n-1) if adj[v].bit_count() < 3]
                for size in range(1, min(3, len(available)) + 1):
                    for links in itertools.combinations(available, size):
                        extended = adj[:] + [sum(1 << v for v in links)]
                        for v in links:
                            extended[v] |= 1 << (n-1)
                        newer.add(canonical(extended)); attempts += 1
            words = newer
        (folder / f'n{n}.txt').write_text('\n'.join(sorted(words)) + '\n')
        print(json.dumps(dict(n=n, graphs=len(words), candidates=attempts,
                              seconds=time.monotonic()-start)), flush=True)


if __name__ == '__main__':
    main()
