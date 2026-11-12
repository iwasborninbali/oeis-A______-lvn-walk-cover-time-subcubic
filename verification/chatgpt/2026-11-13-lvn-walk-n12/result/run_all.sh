#!/usr/bin/env bash
# Reproduce the complete independent verification, with four concurrent n=12 workers.
set -euo pipefail
cd "$(dirname "$0")"
g++ -O3 -std=c++20 -DNDEBUG -o generate generate.cpp
g++ -O3 -std=c++20 -DNDEBUG -o walk walk.cpp
/usr/bin/time -f 'generation wall_seconds=%e peak_rss_kb=%M' \
  ./generate . 12 > generation.log 2> generation.progress
/usr/bin/time -f 'n1_to_n11 wall_seconds=%e peak_rss_kb=%M' \
  ./walk . 1 11 > walk_n1_11.log 2> walk_n1_11.progress
mkdir -p chunks
/usr/bin/time -f 'n12_parallel wall_seconds=%e peak_rss_kb=%M' \
  bash -c 'seq 0 19 | xargs -P 4 -I "{}" bash -c '\''
    i="$1"; off=$((i*1000));
    if [ "$i" -eq 19 ]; then num=430; else num=1000; fi
    ./walk . 12 12 "$num" "$off" 2000000 \
      > "chunks/chunk_$(printf %02d "$i").log" \
      2> "chunks/chunk_$(printf %02d "$i").progress"
  '\'' _ "{}"' 2> n12_parallel.progress
python replay_witness.py > witness_replay.log
python audit_graphs.py > graph_audit.log
python summarize.py > summary.txt
