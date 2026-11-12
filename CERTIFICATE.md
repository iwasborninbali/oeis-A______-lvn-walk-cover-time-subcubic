# Verification certificate

## Claim

- For n ≥ 1, a(n) is the maximum number of moves before first coverage, taken over all connected simple graphs with maximum degree at most three on n vertices, every start vertex, and every legal tie choice. The offset is 1; a(1)=0.
- Claimed terms, starting at index 1: 0, 1, 3, 7, 11, 17, 27, 34, 45, 57, 74, 90.

## Evidence

| What | Program | Author and date | Coverage | Result |
|---|---|---|---|---|
| Producer | `programs/search.cpp`, `programs/generate_graphs.py` | Source lab AI worker, 2026-11-11; the source commit credits Claude Opus 5.5 but does not identify the individual worker | Catalogue and exact maxima through 12 vertices | All table values reproduced on supplied catalogue. |
| Independent check | `verification/independent_census.py` | Source independent audit agent, 2026-11-11 (individual identity not recorded; source commit credits Claude Opus 5.5); path adapted by OpenAI Codex 2026-11-13 | Independently generated graphs and all four extrema through n=9 | Recomputed rows match; see log. |
| Independent full census | `verification/independent_catalogue.py`, `verification/independent_full.cpp`, `verification/compare_sample.py` | Source independent audit agent, 2026-11-11 (individual identity not recorded; source commit credits Claude Opus 5.5); path adapted by OpenAI Codex 2026-11-13 | Fresh catalogue and exhaustive search through n=12, matched graph-by-graph to producer | All graph extrema matched. |
| Witness check | same independent program | Same auditor | Global time and frequency witnesses at n=12 | Both legal; T=90 for time witness, M=22 for frequency witness. |
| Producer comparison | `verification/compare_replay.py` | OpenAI Codex, 2026-11-13 | All producer per-graph outputs and table columns n≤12 | Matches; this is not an independent search. |

The independent census does not import producer code or read its catalogue; the independent graph-by-graph comparison necessarily reads both independent results and producer results; witness checking necessarily reads the producer's witness data. Both implement the same mathematical rule and vertex-augmentation idea, but use separately written isomorphism tests and search implementations. The isomorphism comparison pairs each independent graph with the producer graph; hence independently searched maxima also validate the tree and cubic columns. No separate tree/cubic extremal trajectory was replayed.

## Replayed for this repository

2026-11-13, macOS Darwin arm64, Python 3.14.6 and Apple clang. These runs were performed in the sibling `oeis-A______-lvn-walk-cover-time-subcubic`; the same programs, inputs and logs are copied into this repository. Commands and full recorded outputs are in `verification/logs/`. The source producer was compiled with `clang++ -std=c++17 -O3 programs/search.cpp -o /tmp/athanor-lvn-search` and executed separately for n=1,...,12 as `/tmp/athanor-lvn-search N data/catalog/nN.txt /tmp/athanor-lvn-replay`; `python3 verification/compare_replay.py /tmp/athanor-lvn-replay` checked all regenerated per-graph results and table columns. Producer timings and output are in `producer.log`; comparison is in `comparison.log`. An equivalent self-contained command is `sh verification/replay_producer.sh`.

`(cd verification && python3 independent_census.py --max-n 9)` produced the rows in `independent.log`; its last row has 531 graphs, T=45, M=14, tree T=43, and no cubic graph. It checked the supplied n=12 global witnesses with T=90 and M=22. See the log for running time and complete output. `python3 check.py --mode witnesses --max-n 12 --results ../data/exact`, run from `verification/`, also replayed all 24 global time and frequency witnesses; output is in `witnesses.log`.

The full audit was compiled from the repository root with `clang++ -std=c++17 -O3 verification/independent_full.cpp -o /tmp/athanor-lvn-independent`, then run from `verification/` as `python3 independent_catalogue.py`, `/tmp/athanor-lvn-independent`, and `python3 compare_sample.py --full`, in that order. The equivalent `sh verification/replay_independent.sh` runs those stages. Independently generated catalogues, exhaustive search and per-graph isomorphism comparison all completed through n=12. See `independent_catalogue.log`, `independent_full.log`, and `independent_comparison.log` for complete output and timings.

## Not covered

No separate tree/cubic extremal trajectory was replayed. No terms after 12 vertices, no asymptotic statement, and no priority claim are certified. Terms beyond n=12 have not been computed.

## Guide's independent check

pending

## Verdict

complete — independent catalogue, exhaustive search, and comparison were replayed through n=12.
