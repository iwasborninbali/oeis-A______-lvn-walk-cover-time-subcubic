#!/usr/bin/env python3
"""Independent Python replay of C++ witness paths, including tie legality."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent

def replay(n, index, start, path):
    row = (ROOT / f'graphs_n{n}.txt').read_text().splitlines()[index]
    adjacency = [int(x) for x in row.split()]
    assert len(adjacency) == n and path[0] == start
    counters = [0] * n
    counters[start] = 1
    coverage_step = 0 if n == 1 else None
    largest_before = 0 if n == 1 else 1
    peak_time = 0 if n == 1 else 0
    for t, (u, v) in enumerate(zip(path, path[1:]), 1):
        neighbours = [j for j in range(n) if (adjacency[u] >> j) & 1]
        assert v in neighbours, f'missing edge, step {t}: {u}->{v}'
        assert counters[v] == min(counters[j] for j in neighbours), f'invalid tie, step {t}'
        counters[v] += 1
        assert coverage_step is None, 'path continues after first coverage'
        if all(counters):
            coverage_step = t
        else:
            if max(counters) > largest_before:
                peak_time = t
                largest_before = max(counters)
    assert coverage_step == len(path)-1
    edges = [(i,j) for i in range(n) for j in range(i+1,n) if (adjacency[i] >> j) & 1]
    return coverage_step, largest_before, peak_time, edges, adjacency

if __name__ == '__main__':
    for typ, fn in [('T', 'chunk_03.log'), ('M', 'chunk_01.log')]:
        s = (ROOT / 'chunks' / fn).read_text()
        line = next(x for x in s.splitlines() if x.startswith(f'WITNESS {typ} '))
        match = re.search(r'graph_index=(\d+) start=(\d+) path=([\d,]+)', line)
        idx, start = int(match[1]), int(match[2])
        path = [int(x) for x in match[3].strip(',').split(',')]
        T, M, peak, edges, rows = replay(12,idx,start,path)
        assert (T == 90 if typ=='T' else M==22)
        print(f'WITNESS {typ}: graph_index={idx}, start={start}, T={T}, M={M}, M_first_at_step={peak}, vertices={len(path)}')
        print('adjacency bitmasks:', *rows)
        print('edges:', edges)
        print('path:', ','.join(map(str,path)))
