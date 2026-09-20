# Kobon N=10 Landscape

> [!IMPORTANT]
> **Scientific audit status — 20 September 2026.**
> This repository has been re-audited independently after a validation failure was discovered in a separate N=14 Kobon project. The N=10 result does **not** inherit that failure: all **72 numbered saved configurations** were independently reconstructed as line arrangements and each contains exactly **25 triangular faces**. No N=14-style double-count was found.
>
> The audit also narrowed several historical claims. This repository validates record-matching 25-triangle constructions; it does **not** prove that 25 is the absolute value of `K(10)`, does not establish a global "deep-well" landscape, and does not prove that a hypothetical 26-triangle configuration is topologically inaccessible.

This repository is preserved as a historical computational study of the **N=10 Kobon Triangle Problem**. It contains the search code, 72 saved 25-triangle configurations, graph-analysis utilities, exploratory sensitivity/symmetry experiments, figures and the historical manuscript.

See **[AUDIT.md](AUDIT.md)** for the repository-specific technical audit and claim-by-claim disposition.

## What survives the audit

- **Saved constructions:** all **72/72** numbered JSON configurations under `solutions/` independently validate as arrangements with exactly **25 triangular faces**.
- **Independent check:** `src/validate_faces.py` counts triangular *faces* by adjacency of consecutive intersections on their three boundary lines. It intentionally does not import or reuse the legacy triangle predicate.
- **Graph diversity:** the 72 configurations form **11 isomorphism classes of the simple intersection graph used by this project**.
- **No N=14-style duplicate:** the legacy solver's 25-count agrees with the independent face count for every numbered N=10 configuration.

Run the independent dataset check with:

```bash
python src/validate_faces.py --all
```

## Scope of the "11 classes" result

The project's intersection graph has one node per pairwise line intersection and connects intersections that are consecutive along a line.

The historical code used a Weisfeiler-Lehman hash as if it were a canonical isomorphism certificate. The audit reproduced the 11 WL buckets and then checked graph isomorphism explicitly within every non-singleton bucket. The classifier has been corrected accordingly.

These are **11 simple intersection-graph isomorphism classes**. That is not the same as proving exactly 11 geometric configurations, isotopy classes or oriented-matroid types; the graph representation deliberately forgets some geometric/combinatorial information.

## Historical optimization result

The historical manuscript reports **20/20 search runs reaching score 25**, described there as "100% convergence".

That statement is now treated as a **campaign-specific historical observation**, not as an algorithmic guarantee:

- the current repository does not retain the per-run logs/seeds needed to reconstruct the 20/20 table;
- `src/main.py` contains the 20 × 100,000-iteration simulated-annealing driver;
- the manuscript additionally describes a Basin-Hopping phase implemented separately in `src/refiner.py`, not in `src/main.py`.

The saved 25-triangle outputs are independently valid; the exact historical convergence statistic is not independently reproducible from the current public artifacts alone.

## Exploratory landscape and symmetry work

`src/breather.py`, `src/force_symmetry.py`, `src/soft_symmetry.py` and the associated figures are retained as exploratory experiments.

The Breather scan is a **one-dimensional sensitivity slice** through parameter space. A sharp score change along that path does not prove a narrow basin in the full space, a "deep well", topological isolation, or a combinatorial impossibility of reaching 26 continuously.

Likewise, the finite symmetry searches report what those search procedures found; they do not establish global maxima under all possible symmetry constraints.

## Relation to the retracted N=14 project

The separate repository `falker47/kobon-n14-discovery` was retracted after a validator double-counted one topological region. Its historical CPU validator used the same broad signed-separation idea as the legacy N=10 triangle predicate, which made an independent N=10 audit necessary.

For N=10, the independent arrangement-face criterion agrees with the legacy count on all 72 numbered saved configurations. The N=14 failure therefore exposed a **validation-design risk**, but no corresponding N=10 counting error was found in this dataset.

## Repository structure

- `src/` — historical search/analysis code plus the independent face validator.
- `solutions/` — 72 numbered record-matching 25-triangle configurations and additional experiment outputs.
- `images/` — historical visualizations.
- `ANALYSIS.md` — audit-corrected scientific post-mortem.
- `AUDIT.md` — detailed 2026 repository-specific audit.
- `paper assets/paper.md` — historical manuscript source with an audit notice.
- `paper.pdf` — historical compiled manuscript snapshot; **its stronger landscape interpretations are superseded by the 2026 audit**.

## Historical usage

The original search entry point remains:

```bash
python src/main.py --lines 10 --iterations 100000 --runs 20
```

The code and historical artifacts are intentionally retained rather than rewritten into a different research project. For the current scientific status, use this README and `AUDIT.md` as the authoritative entry points.
