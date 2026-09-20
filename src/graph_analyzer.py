"""
Intersection-graph analysis for the N=10 Kobon configurations.

Audit note (2026-09-20):
- triangular faces are derived from adjacency in the line arrangement;
- Weisfeiler-Lehman hashes are fingerprints / candidate buckets, not canonical
  isomorphism certificates;
- exact NetworkX graph-isomorphism checks are used inside every WL bucket;
- by default only the 72 numbered variant<index>*.json files are classified.
"""

import glob
import json
import os
import re
from collections import defaultdict
from itertools import combinations

import numpy as np

try:
    import networkx as nx
    from networkx.algorithms.graph_hashing import weisfeiler_lehman_graph_hash
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("WARNING: networkx not installed. Install with: pip install networkx")


def compute_intersections(lines):
    """Return pairwise intersections and a mask for non-parallel pairs."""
    n = len(lines)
    a = lines[:, 0]
    b = lines[:, 1]
    c = lines[:, 2]

    denom = a[:, None] * b[None, :] - a[None, :] * b[:, None]
    valid = np.abs(denom) > 1e-10
    np.fill_diagonal(valid, False)

    safe = np.where(valid, denom, 1.0)
    x = (b[:, None] * c[None, :] - b[None, :] * c[:, None]) / safe
    y = (a[None, :] * c[:, None] - a[:, None] * c[None, :]) / safe

    points = np.zeros((n, n, 2))
    points[:, :, 0] = x
    points[:, :, 1] = y
    return points, valid


def extract_intersection_graph(lines):
    """
    Build the simple intersection graph.

    Nodes are pairwise line intersections (i, j).  Edges connect consecutive
    intersections along a line.  A triangular face is then a triple of lines
    whose three pair-intersection nodes are connected by the three arrangement
    edges required for that face.
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required for graph analysis")

    n = len(lines)
    points, valid = compute_intersections(lines)
    G = nx.Graph()

    for i in range(n):
        for j in range(i + 1, n):
            if valid[i, j]:
                G.add_node((i, j), line_pair=(i, j), pos=tuple(points[i, j]))

    for line_idx in range(n):
        intersections = []
        a, b, _c = lines[line_idx]
        direction = np.array([b, -a])

        for other in range(n):
            if other == line_idx:
                continue
            i, j = sorted((line_idx, other))
            if not valid[i, j]:
                continue
            pt = points[i, j]
            intersections.append((float(np.dot(pt, direction)), (i, j)))

        intersections.sort(key=lambda item: item[0])
        for left, right in zip(intersections, intersections[1:]):
            G.add_edge(left[1], right[1], line=line_idx)

    triangle_set = set()
    for i, j, k in combinations(range(n), 3):
        nij = (i, j)
        nik = (i, k)
        njk = (j, k)
        if nij not in G or nik not in G or njk not in G:
            continue
        if G.has_edge(nij, nik) and G.has_edge(nij, njk) and G.has_edge(nik, njk):
            triangle_set.add(frozenset((i, j, k)))

    return G, triangle_set


def wl_fingerprint(G, triangle_set=None):
    """
    Return an isomorphism-invariant WL fingerprint.

    This is deliberately called a fingerprint, not a canonical hash:
    equal WL fingerprints do not by themselves prove graph isomorphism.
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required for graph analysis")

    n_triangles = len(triangle_set) if triangle_set is not None else 0
    H = G.copy()
    for node in H.nodes():
        H.nodes[node]["degree"] = H.degree(node)
    digest = weisfeiler_lehman_graph_hash(H, node_attr="degree", iterations=3)
    return f"{n_triangles}_{digest}"


def canonical_hash(G, triangle_set=None):
    """Backward-compatible alias. Prefer wl_fingerprint(); this is not canonical."""
    return wl_fingerprint(G, triangle_set)


def load_configuration(filepath):
    with open(filepath, "r", encoding="utf-8") as handle:
        return np.array(json.load(handle)["lines"], dtype=float)


def numbered_solution_files(solution_dir="solutions"):
    """Return the audited 72-file corpus: variant0 ... variant71 (suffixes allowed)."""
    rx = re.compile(r"^variant\d.*\.json$")
    return sorted(
        path
        for path in glob.glob(os.path.join(solution_dir, "variant*.json"))
        if rx.match(os.path.basename(path))
    )


def _split_bucket_by_exact_isomorphism(items):
    """
    Split one WL bucket using exact graph isomorphism.

    items: list of dicts containing path, graph and triangles.
    """
    classes = []
    for item in items:
        placed = False
        for cls in classes:
            representative = cls[0]
            if nx.is_isomorphic(item["graph"], representative["graph"]):
                cls.append(item)
                placed = True
                break
        if not placed:
            classes.append([item])
    return classes


def classify_configurations(solution_dir="solutions", include_extras=False):
    """
    Classify configurations by exact isomorphism of the simple intersection graph.

    WL fingerprints are used only to reduce the number of exact comparisons.
    """
    if not HAS_NETWORKX:
        raise ImportError("networkx required for classification")

    files = numbered_solution_files(solution_dir)
    if include_extras:
        numbered = set(files)
        files.extend(
            path for path in sorted(glob.glob(os.path.join(solution_dir, "variant*.json")))
            if path not in numbered
        )

    buckets = defaultdict(list)
    errors = []

    for filepath in files:
        try:
            lines = load_configuration(filepath)
            G, triangles = extract_intersection_graph(lines)
            fp = wl_fingerprint(G, triangles)
            buckets[fp].append({
                "path": filepath,
                "graph": G,
                "triangles": triangles,
            })
        except Exception as exc:
            errors.append((filepath, str(exc)))

    exact_classes = []
    for bucket in buckets.values():
        exact_classes.extend(_split_bucket_by_exact_isomorphism(bucket))

    exact_classes.sort(key=lambda cls: (-len(cls), cls[0]["path"]))
    families = {
        f"class_{idx:02d}": [item["path"] for item in cls]
        for idx, cls in enumerate(exact_classes, 1)
    }

    stats = {
        "total_files": len(files),
        "unique_graphs": len(exact_classes),
        "wl_buckets": len(buckets),
        "largest_family": max((len(cls) for cls in exact_classes), default=0),
        "singletons": sum(1 for cls in exact_classes if len(cls) == 1),
        "errors": len(errors),
    }
    return families, stats


def print_classification_report(families, stats):
    print("\n" + "=" * 64)
    print("EXACT SIMPLE INTERSECTION-GRAPH CLASSIFICATION")
    print("=" * 64)
    print(f"Configurations analyzed: {stats['total_files']}")
    print(f"WL candidate buckets:    {stats['wl_buckets']}")
    print(f"Exact graph classes:     {stats['unique_graphs']}")
    print(f"Largest class:           {stats['largest_family']}")
    print(f"Singleton classes:       {stats['singletons']}")
    print(f"Errors:                  {stats['errors']}")

    for class_id, members in families.items():
        print(f"\n{class_id} ({len(members)} members)")
        for member in members:
            print(f"  - {member}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))
    families, stats = classify_configurations("solutions")
    print_classification_report(families, stats)
