#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
c++ -std=c++17 -O3 "$root/programs/search.cpp" -o "$tmp/search"
n=1
while [ "$n" -le 12 ]; do
  "$tmp/search" "$n" "$root/data/catalog/n$n.txt" "$tmp"
  n=$((n+1))
done
python3 "$root/verification/compare_replay.py" "$tmp"
