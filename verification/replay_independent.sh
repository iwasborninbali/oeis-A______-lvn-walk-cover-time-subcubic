#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root/verification"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
c++ -std=c++17 -O3 independent_full.cpp -o "$tmp/independent_full"
python3 independent_catalogue.py
"$tmp/independent_full"
python3 compare_sample.py --full
