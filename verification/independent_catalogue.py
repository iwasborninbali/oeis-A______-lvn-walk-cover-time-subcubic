"""Generate a fresh catalogue, independent of the supplied canonical labeller."""
import json
import resource
import time
from pathlib import Path
from independent_census import extend, word

resource.setrlimit(resource.RLIMIT_CPU, (450, 450))
folder = Path('independent_catalogue')
folder.mkdir(exist_ok=True)
graphs = [(0,)]
start = time.monotonic()
for n in range(1, 13):
    if n > 1:
        graphs = extend(graphs)
    (folder / f'n{n}.txt').write_text('\n'.join(map(word, graphs)) + '\n')
    print(json.dumps(dict(n=n, classes=len(graphs), seconds=time.monotonic()-start,
                          cpu=resource.getrusage(resource.RUSAGE_SELF).ru_utime)), flush=True)
