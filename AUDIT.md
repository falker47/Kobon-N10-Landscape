# Repository-specific scientific audit — 20 September 2026

## Scope

This audit was performed after a separate N=14 Kobon project was retracted because its validation pipeline double-counted one topological region as two triangles. The N=10 repository was therefore re-examined independently rather than assumed valid or invalid by analogy.

The audit covered the 72 numbered JSON configurations under `solutions/`; the geometry, optimizer/refiner and graph-analysis code; the convergence, diversity, symmetry and Breather claims; and the corresponding historical validation pattern in `falker47/kobon-n14-discovery`.

## 1. The saved 25-triangle configurations survive independent validation

The historical solver counts a triple of lines as a triangle when no other line strictly separates its three vertices. That is also the conceptual pattern used by the historical N=14 validator, so simply rerunning `KobonSolver.find_triangles()` would not be an independent check.

For this audit, the 72 numbered N=10 configurations were revalidated from the arrangement itself:

1. normalize every line;
2. compute every pairwise intersection;
3. sort the nine intersections along each line;
4. count a triple `(i, j, k)` only when its two vertices are consecutive on line `i`, consecutive on line `j`, and consecutive on line `k`.

In a simple line arrangement, those three adjacency conditions mean that the three sides are actual edges of the arrangement and therefore bound a triangular face.

**Result: 72/72 files contain exactly 25 triangular faces.** The independent face count agrees with the declared score and with the legacy solver for every numbered configuration. No extra legacy-solver triangle was found in any of the 72 files, so the N=14 double-counting failure was **not reproduced in this N=10 corpus**.

A standalone implementation is preserved at `src/validate_faces.py`:

```bash
python src/validate_faces.py --all
```

The smallest adjacent-intersection separation observed in the normalized audit corpus occurs in `solutions/variant36_singleton.json` (about `1.22e-5` in the line-ordering parameter). This makes that configuration relatively numerically tight, but it does not change its 25-face count in the audit.

### What this validates — and what it does not

This validates the **saved constructions** as 25-triangle arrangements. It is not an exhaustive proof that `K(10)=25`, and it does not prove that a 26-triangle arrangement cannot exist.

Accordingly, phrases such as "global maximum" are inappropriate unless they refer explicitly to the best score observed by a stated search procedure.

## 2. The dataset contains 11 simple intersection-graph isomorphism classes

The repository's graph representation uses one vertex for each pairwise line intersection and an edge between consecutive intersections along a line.

The original classifier grouped configurations by a 3-iteration Weisfeiler-Lehman (WL) hash and called the result a "canonical hash". A WL hash is a useful isomorphism invariant, but equality of hashes alone is not a proof of graph isomorphism.

The audit therefore:

1. independently reconstructed the intersection graphs and reproduced **11 distinct WL classes** across the 72 configurations;
2. within every non-singleton WL class, explicitly found adjacency-preserving graph isomorphisms to a class representative.

**Result: the 72 saved configurations form 11 isomorphism classes of the repository's simple intersection graph.**

This is intentionally narrower than "11 geometrically distinct configurations" or "11 isotopy classes". Simple graph isomorphism is coarser than oriented-matroid / isotopy information and discards metric geometry. The repository therefore does **not** establish that the number of geometric, isotopy or oriented-matroid types is exactly 11.

`src/graph_analyzer.py` is corrected so that WL fingerprints are treated as candidate buckets and exact NetworkX graph-isomorphism checks split those buckets when necessary.

## 3. "100% convergence" is a historical experimental report, not a guarantee

The manuscript reports 20 successful runs out of 20, each reaching score 25, and labels this "100% convergence".

The current public repository does not contain per-run logs, seeds or a retained results table from that campaign. In addition:

- `src/main.py` defaults to 20 independent simulated-annealing runs of 100,000 iterations;
- the manuscript describes each run as also being followed by 1,000 Basin-Hopping kicks;
- `src/main.py` does not execute that Basin-Hopping phase;
- `src/refiner.py` contains a separate 1,000-kick refinement workflow and points to historical input/output paths that are not present in the current tree.

Therefore the precise 20/20 statistic cannot be reconstructed from the versioned artifacts alone. It is retained as a **historically reported observation for a particular campaign**, not as a reproducible guarantee of the algorithm and not as evidence that the basin probability is 1.

## 4. Landscape, "deep well" and topological-barrier claims were too strong

The Breather experiment varies one scalar parameter: it selects five "inner" lines and scales their `c` coefficients along a one-dimensional path. The historical plot shows the score changing sharply near the saved configuration along that chosen path.

That supports only a local statement: **the score is sensitive along the tested one-dimensional perturbation path.**

It does **not** by itself establish the width or volume of a basin in the full parameter space, a "deep well", topological isolation, the absence of a continuous path to a hypothetical score-26 arrangement, or a proof that the 25→26 barrier is combinatorial rather than metric.

Those stronger conclusions are now treated as exploratory interpretations / hypotheses.

The same caution applies to the symmetry experiments. The hard-symmetry script performs a finite stochastic search inside one Y-axis-reflection parameterization; finding 18 there does not prove that 18 is the maximum over all symmetric arrangements. The soft-symmetry experiment is likewise exploratory.

## 5. Independence and circularity

Before this audit, there was no independent validator in the repository:

- `optimizer.py` scores candidates with `KobonSolver.find_triangles()`;
- `refiner.py` uses the same solver;
- `analyzer.py` "verifies" scores with the same solver;
- `graph_analyzer.py` historically reimplemented essentially the same signed-separation triangle predicate.

Solver and validator therefore shared the central assumption. The new arrangement-face validator intentionally removes that circularity for the saved dataset.

## 6. Disposition of the main claims

| Claim | Audit status |
|---|---|
| The 72 numbered saved configurations have 25 triangles | **Supported**: 72/72 independently validated as 25 triangular faces |
| The N=14 double-count also invalidates N=10 | **Not supported**: no analogous discrepancy found in the N=10 corpus |
| There are 11 simple intersection-graph classes among the 72 files | **Supported**, with exact isomorphism checks inside WL buckets |
| There are exactly 11 geometric / isotopy / oriented-matroid types | **Not established** |
| "100% convergence" | **Historical 20/20 report**; campaign evidence is not fully retained/reconstructable |
| 25 is a proven global maximum | **Not established by this repository** |
| The configurations are proven "deep wells" / topologically isolated | **Not established** |
| The barrier to 26 is proven combinatorial rather than metric | **Exploratory hypothesis, not a proof** |
| Forced symmetry has proven maximum 18 | **Not established**; 18 is the best result of the retained finite search procedure |

## Archival interpretation

The scientifically durable part of this repository is the set of valid 25-triangle constructions, the code that generated/explored them, and the 11-class simple-graph diversity result. The stronger landscape narrative is preserved for historical transparency but is explicitly scoped as exploratory rather than established.
