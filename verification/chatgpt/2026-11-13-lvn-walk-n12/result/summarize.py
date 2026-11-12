#!/usr/bin/env python3
"""Merge disjoint exhaustive n=12 chunks and compare all five claimed rows."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent
ref_counts=[1,1,2,6,10,29,64,194,531,1733,5524,19430]
ref_T=[0,1,3,7,11,17,27,34,45,57,74,90]
ref_M=[0,1,2,3,5,7,8,8,14,16,22,22]
ref_treeT=[0,1,3,7,11,17,27,31,43,57,63,83]
ref_cubicT={4:3,6:8,8:15,10:26,12:42}

def read_result(text):
    row=next(line for line in text.splitlines() if line.startswith('RESULT '))
    values = {k: int(v) for k,v in re.findall(r'(\w+)=(\d+)',row)}
    values['seconds'] = float(re.search(r'seconds=([0-9.]+)', row).group(1))
    return values

rows=[]
for n in range(1,12):
    r=next(read_result(line) for line in (ROOT/'walk_n1_11.log').read_text().splitlines() if line.startswith(f'RESULT n={n} '))
    assert r['complete']==1 and r['skipped']==0 and r['processed']==ref_counts[n-1]
    rows.append(r)

chunks=[]
for i in range(20):
    r=read_result((ROOT/'chunks'/f'chunk_{i:02d}.log').read_text())
    expect=430 if i==19 else 1000
    assert r['processed']==expect and r['skipped']==0 and r['seen']==i*1000+expect
    chunks.append(r)
assert sum(r['processed'] for r in chunks)==19430
n12={k:max(r[k] for r in chunks) for k in ('T','M','treeT','cubicT')}
n12.update(n=12,processed=sum(r['processed'] for r in chunks),states=sum(r['states'] for r in chunks),seconds=sum(r['seconds'] for r in chunks),trees=sum(r['trees'] for r in chunks),cubics=sum(r['cubics'] for r in chunks))
rows.append(n12)
for n,r in enumerate(rows,1):
    assert r['T']==ref_T[n-1] and r['M']==ref_M[n-1] and r['treeT']==ref_treeT[n-1]
    if n in ref_cubicT: assert r['cubicT']==ref_cubicT[n]
    print(f"n={n:2d} graphs={r['processed']:5d} T={r['T']:2d} M={r['M']:2d} treeT={r['treeT']:2d} cubicT={str(r['cubicT']) if n%2==0 and n>=4 else '-':>2} states={r['states']:10d}")
print('n12 total worker seconds=',sum(r['seconds'] for r in chunks))
print('n12 graphs=',n12['processed'],'trees=',n12['trees'],'cubic=',n12['cubics'])
print('ALL FIVE ROWS MATCH; ALL GRAPHS ANALYZED; ZERO SKIPPED')
