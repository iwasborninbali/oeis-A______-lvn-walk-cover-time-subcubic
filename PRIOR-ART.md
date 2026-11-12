# Prior art and credit

OEIS searches on 2026-11-13, JSON endpoint `https://oeis.org/search`, using the exact `q` strings below. Counts are numbers returned on the first page, not necessarily total counts; short searches can be capped at 10. Removing the first terms tests index shifts; the cubic index n labels 2n vertices, so its consecutive values are also the obvious graph-order re-indexing.

- `0,1,3,7,11,17,27,34,45,57,74,90`: 0 result(s) on the returned page.
- `1,3,7,11,17,27,34,45,57,74,90`: 0 result(s) on the returned page.
- `3,7,11,17,27,34,45,57,74,90`: 0 result(s) on the returned page.
- `least visited neighbor graph`: 2 result(s) on the returned page.
- `least frequently visited vertex walk`: 0 result(s) on the returned page.
- `node counting cover time`: 10 result(s) on the returned page.
- `id:A243393`: 1 result(s) on the returned page.

No complete match was returned for the full numeric query; this is a bounded search, not a proof of novelty. OEIS [A243393](https://oeis.org/A243393) gives 1,1,2,6,10,29,64,194,531,1733,5524,19430, the same connected subcubic graph counts (encoded there as cubic graphs with semi-edges). This is a catalogue consistency check, not a claim that it records walk extrema.

The short cubic tail 8,15,26,42 occurs in [A000125](https://oeis.org/A000125) (cake numbers), [A133551](https://oeis.org/A133551) (binary strings) and [A129961](https://oeis.org/A129961) (a triangular-array diagonal); those records begin their matching run with 8 rather than this candidate's preceding 3. [A011890](https://oeis.org/A011890) contains 3,7,15,26,42, differing at the second term. Shared tails do not imply identical definitions or continuations.

Prior literature was identified and assessed in the source `solution/result.md` and `audit/literature_search.md`; citations below are links, not copies:

- [Akash et al., JGAA 21 (2017), 371–387](https://doi.org/10.7155/jgaa.00421) study LFV-v and formulate a subcubic conjecture; their result is not this finite extrema table.
- [Koenig, COLT 2010](https://www.learningtheory.org/colt2010/conference-website/papers/OpenProblemKoenig.pdf) poses bounded-degree node-counting questions, including adversarial ties.
- [Koenig and Szymanski, AAAI 1999](https://cdn.aaai.org/AAAI/1999/AAAI99-102.pdf) treat a directed Eulerian arc-subdivision special case, not this general subcubic census.
- [Koenig, Szymanski and Liu (2001)](https://idm-lab.org/bib/abstracts/papers/amai01.pdf) establish results for real-time search and counterexamples for node counting on trees of growing degree.
- [Cooper et al. (2011)](https://www.labri.fr/perso/ilcinkas/publications/DisComp-ICALP09.pdf) study least-used edge walks, a different selection rule.
- [Wagner, Lindenbaum and Bruckstein (1999)](https://freddy.cs.technion.ac.il/wp-content/uploads/2018/01/Distributed-Covering-by-Ant-Robots.pdf) analyze timestamp-based vertex and edge ant walks.
- [Avin and Krishnamachari (2006)](https://tzin.bgu.ac.il/~avin/papers/MSWiM06-CR.pdf) use sampled, degree-normalized choices, a different policy.
- [Wagner, Lindenbaum and Bruckstein (1998)](https://freddy.cs.technion.ac.il/wp-content/uploads/2018/01/Efficiently-searching-a-graph-by-a-smell-oriented-vertex.pdf) analyze a different label-update walk; [Yanovski, Wagner and Bruckstein (2003)](https://freddy.cs.technion.ac.il/wp-content/uploads/2018/02/A-Distributed-Ant-Algorithm-for.pdf) analyze cyclic next-exit pointers, not this vertex rule.

The original catalogue and finite table, and the separately authored audit, are lab work dated 2026-11-11. No earlier source for these exact maxima is claimed to have been ruled out. Terms beyond n=12 have not been computed.
