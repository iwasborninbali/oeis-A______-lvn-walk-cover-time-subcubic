"""Check regenerated producer per-graph extrema and derive all table columns."""
import csv, json, sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
replayed = Path(sys.argv[1])
rows = list(csv.DictReader((root/'data/table.csv').open()))
for row in rows:
    n = int(row['n'])
    original = [json.loads(x) for x in (root/f'data/exact/n{n}.jsonl').read_text().splitlines()]
    fresh = [json.loads(x) for x in (replayed/f'n{n}.jsonl').read_text().splitlines()]
    assert original == fresh, n
    trees, cubic = [], []
    for g in fresh:
        degrees=[0]*n
        for bit, (i,j) in zip(g['word'], ((i,j) for i in range(n) for j in range(i+1,n))):
            if bit == '1': degrees[i]+=1; degrees[j]+=1
        t=max(g['times'])
        if sum(degrees)==2*(n-1): trees.append(t)
        if all(d==3 for d in degrees): cubic.append(t)
    assert len(fresh)==int(row['connected_simple_subcubic_graphs'])
    assert max(max(g['times']) for g in fresh)==int(row['worst_first_cover_moves'])
    assert max(max(g['frequencies']) for g in fresh)==int(row['worst_frequency_before_cover'])
    assert max(trees)==int(row['tree_worst_first_cover'])
    assert len(cubic)==int(row['cubic_graphs'] or 0)
    if cubic: assert max(cubic)==int(row['cubic_worst_first_cover'])
    print(f'n={n}: {len(fresh)} graphs; all per-graph producer results and all table columns match')
