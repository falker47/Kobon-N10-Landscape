# Kobon N=10 — audit-corrected scientific post-mortem

> **Status: historical computational study, re-audited 20 September 2026.**
> The 72 numbered saved configurations remain valid 25-triangle arrangements under an independent face-based check. Several stronger interpretations in the original post-mortem have been narrowed because the retained evidence does not support them as proofs.

For full methodology and claim-by-claim disposition, see [AUDIT.md](AUDIT.md).

## 1. What is established

### 1.1 The saved 25-triangle constructions are valid

All 72 numbered files in `solutions/` were independently checked by reconstructing the line arrangement and counting triangular **faces** from adjacency of consecutive intersections on each boundary line.

**Result: 72/72 independently count to 25.**

This check does not reuse `KobonSolver.find_triangles()` and therefore is not circular with the historical optimizer. No discrepancy analogous to the N=14 double-counting failure was found.

This result establishes the validity of the saved 25-triangle constructions. It does **not** prove that 25 is the global mathematical value of `K(10)` or exclude a 26-triangle construction.

### 1.2 The dataset has 11 simple intersection-graph classes

The 72 numbered configurations were reconstructed as simple intersection graphs:

- nodes = pairwise line intersections;
- edges = adjacency of consecutive intersections along a line.

The historical code produced 11 Weisfeiler-Lehman hash groups. Because equal WL hashes are not themselves an isomorphism proof, the 2026 audit additionally performed explicit graph-isomorphism checks within every non-singleton WL group.

**Result: 11 simple intersection-graph isomorphism classes across the 72 saved configurations.**

This is a statement about the graph representation used here. It must not be promoted to "11 geometrically distinct configurations", "11 isotopy classes" or "11 oriented-matroid types": those are finer equivalence notions.

## 2. Historical search campaign

The historical manuscript reports 20 independent trials reaching score 25 out of 20 trials, hence the phrase **"100% convergence"**.

That is best read as:

> 20/20 successes were reported for the historical campaign described by the manuscript.

It is **not** a general convergence theorem or probability estimate for the optimizer.

The current repository does not preserve the per-run logs, seeds and result table needed to reconstruct that campaign exactly. There is also a workflow mismatch in the retained artifacts: `src/main.py` implements the 20 × 100,000-iteration simulated-annealing driver, whereas the manuscript describes an additional 1,000-kick Basin-Hopping phase that lives separately in `src/refiner.py`.

Accordingly, the 20/20 number is retained for historical transparency but not used as an independently verified repository-level result.

## 3. Local sensitivity: what the Breather scan shows

The Breather experiment scales the `c` coefficients of five selected "inner" lines while leaving the remaining lines fixed. It is therefore a **one-dimensional path through a much larger parameter space**.

The historical scan reports a score of 25 at the baseline and lower scores after small changes along this particular path. That is legitimate evidence of sensitivity **along that path**.

It does not establish:

- a full-dimensional basin width or volume;
- a "deep well" in a rigorous optimization-landscape sense;
- topological isolation of a 25-triangle arrangement;
- absence of a continuous route to a hypothetical 26-triangle arrangement;
- proof that the 25→26 barrier is combinatorial rather than metric.

Those statements should be treated as hypotheses suggested by the experiment, not conclusions demonstrated by it.

## 4. Symmetry experiments

The hard-symmetry experiment forced a specific Y-axis reflection parameterization and used a finite stochastic search. Its best retained result was 18 under that procedure.

The soft-symmetry experiment retained score 25 while penalizing asymmetry.

These experiments are useful exploratory probes, but they do not prove a global maximum of 18 under all symmetric arrangements and do not establish that symmetry, in general, cannot participate in a 25- or 26-triangle construction.

## 5. Validation architecture

The historical validation pipeline was not independent:

- `optimizer.py` uses `KobonSolver.find_triangles()` as its objective;
- `refiner.py` uses the same solver;
- `analyzer.py` rechecks scores with the same solver;
- the original `graph_analyzer.py` used essentially the same signed-separation triangle condition.

That shared logic was a concern after the separate N=14 project failed under a topological double-count.

The repository now includes `src/validate_faces.py`, which reconstructs arrangement edges instead of reusing the solver predicate:

```bash
python src/validate_faces.py --all
```

The graph classifier has also been corrected: WL hashes now serve only as candidate buckets, followed by exact NetworkX isomorphism checks.

## 6. Current interpretation

The durable results of this project are:

1. a corpus of **72 independently validated 25-triangle N=10 arrangements**;
2. **11 simple intersection-graph isomorphism classes** within that corpus;
3. historical search, sensitivity and symmetry experiments that are useful as exploratory records.

The following former wording is superseded:

- "proved global maximum";
- "proved deep well";
- "topologically isolated";
- "barrier to 26 is proven combinatorial";
- "11 geometrically distinct configurations";
- "100% convergence" when presented without the explicit historical 20/20 campaign scope.

The repository is preserved to keep the computational record, including the stronger historical narrative, transparent rather than erasing it.
