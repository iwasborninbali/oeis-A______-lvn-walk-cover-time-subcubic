# Independent recount: worst cases of the least-visited-neighbour walk on small subcubic graphs (n <= 12)

You are asked to check a computational claim **independently**: write your own programs from the definition below, run them
in your container, and report. This archive deliberately contains only this brief.

## Definitions
- Graphs: finite, simple, undirected, **connected**, maximum degree at most 3 ("subcubic"), on n vertices, up to isomorphism.
- The walk: choose a start vertex x0 and set its counter to 1, all other counters to 0. At each step the walker moves along an
  edge from its current vertex to **any** neighbour whose counter is smallest among the neighbours, and that neighbour's counter
  increases by 1. Ties may be broken arbitrarily (any history-dependent choice is allowed). There is no waiting.
- T = number of moves until every counter is positive (first coverage). For n = 1, T = 0.
- M = the largest counter value at any time t < T (the initial counter 1 of the start vertex counts; for n = 1, M = 0).
- For a graph, maximise over all starts and all tie choices. Then maximise over graphs.

## Claim to check (n = 1..12)
| sequence | values for n = 1..12 |
|---|---|
| number of connected subcubic graphs (OEIS A243393) | 1, 1, 2, 6, 10, 29, 64, 194, 531, 1733, 5524, 19430 |
| max T over all such graphs | 0, 1, 3, 7, 11, 17, 27, 34, 45, 57, 74, 90 |
| max M over all such graphs | 0, 1, 2, 3, 5, 7, 8, 8, 14, 16, 22, 22 |
| max T over trees (max degree <= 3) | 0, 1, 3, 7, 11, 17, 27, 31, 43, 57, 63, 83 |
| max T over cubic graphs (n even, n >= 4) | n = 4, 6, 8, 10, 12: 3, 8, 15, 26, 42 |

Note that T and M are maximised separately (the maximisers can differ).

## What to do
1. Report your container: `nproc`, memory, compiler versions.
2. Generate the graphs with your own program (no external generator such as nauty unless you also write a check of the counts;
   say what you used). Compare the counts with the first row.
3. For every graph compute max T and max M over all starts and tie choices exactly (state the method: e.g. exhaustive DFS over
   walk states with memoisation on (position, counter vector); counters can be capped or not, explain why your method is exact).
4. Report all five rows for n = 1..12 (or as far as you get), and for n = 12 one graph, start and tie sequence attaining T = 90 and one attaining M = 22.
5. If the full run takes long, start it **in the background** with checkpoints and progress files, use all cores, and set
   yourself a reminder, scheduled task or cron job to report progress if you can (say if you cannot; we will ask in this chat).
   Reply now with what you started and an estimate; do not wait for the end in this reply.
6. At the end: results, run times, exact commands, SHA-256 of your source files and logs, and the source code itself in the reply.

Answer in English. Be exact; say plainly what was not finished or not checked.
