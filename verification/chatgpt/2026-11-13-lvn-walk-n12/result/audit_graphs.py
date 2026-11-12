#!/usr/bin/env python3
"""Independent structural audit of the generated graph files."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
EXPECTED = [0,1,1,2,6,10,29,64,194,531,1733,5524,19430]
for n in range(1,13):
    rows = (ROOT / f'graphs_n{n}.txt').read_text().splitlines()
    assert len(rows)==EXPECTED[n]
    tree=cubic=0
    for row in rows:
        adj=list(map(int,row.split()))
        assert len(adj)==n
        assert all(0<=a<(1<<n) for a in adj)
        assert all(not (adj[i]>>i&1) and adj[i].bit_count()<=3 for i in range(n))
        assert all(bool(adj[i]>>j&1)==bool(adj[j]>>i&1) for i in range(n) for j in range(n))
        seen={0};todo=[0]
        while todo:
            i=todo.pop()
            for j in range(n):
                if (adj[i]>>j&1) and j not in seen:
                    seen.add(j);todo.append(j)
        assert len(seen)==n
        tree+=sum(a.bit_count() for a in adj)==2*(n-1)
        cubic+=all(a.bit_count()==3 for a in adj)
    print(f'n={n} graphs={len(rows)} trees={tree} cubic={cubic} valid=yes')
