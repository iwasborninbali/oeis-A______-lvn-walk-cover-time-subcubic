"""Match our independently generated graphs to the supplied data by isomorphism."""
import argparse
import json
import resource
import time
from collections import defaultdict
from pathlib import Path
from independent_census import colors, isomorphic


def decode(n, word):
    assert len(word) == n * (n - 1) // 2
    adj = [0] * n
    p = 0
    for u in range(n):
        for v in range(u + 1, n):
            if word[p] == '1':
                adj[u] |= 1 << v
                adj[v] |= 1 << u
            p += 1
    return tuple(adj)


parser = argparse.ArgumentParser()
parser.add_argument('--full', action='store_true')
args = parser.parse_args()
resource.setrlimit(resource.RLIMIT_CPU, (300, 300))
started = time.monotonic()
maximum = 12 if args.full else 9
input_file = 'independent_full_results.jsonl' if args.full else 'independent_graph_results.jsonl'
output_file = 'full_comparison.json' if args.full else 'sample_comparison.json'
ours = [json.loads(line) for line in Path(input_file).read_text().splitlines()]
rows = []
for n in range(1, maximum + 1):
    theirs = [json.loads(line) for line in Path(f'../data/exact/n{n}.jsonl').read_text().splitlines()]
    buckets = defaultdict(list)
    for index, row in enumerate(theirs):
        g = decode(n, row['word'])
        c, signature = colors(g)
        buckets[signature].append((index, g, c, row))
    matched = set()
    for row in (r for r in ours if r['n'] == n):
        g = decode(n, row['word'])
        c, signature = colors(g)
        matches = [(index, old) for index, oldg, oldc, old in buckets[signature]
                   if isomorphic(g, c, oldg, oldc)]
        assert len(matches) == 1
        index, old = matches[0]
        assert index not in matched
        matched.add(index)
        assert row['T'] == max(old['times'])
        assert row['M'] == max(old['frequencies'])
        if args.full:
            assert row['nonterminal_states'] == old['states']
    assert len(matched) == len(theirs)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rows.append(dict(n=n, classes_matched=len(matched), all_per_graph_extrema_equal=True,
                     cpu_seconds=usage.ru_utime + usage.ru_stime,
                     elapsed_seconds=time.monotonic() - started))
    print(json.dumps(rows[-1]), flush=True)
Path(output_file).write_text(json.dumps(rows, indent=2) + '\n')
