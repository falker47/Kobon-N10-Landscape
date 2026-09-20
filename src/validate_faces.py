#!/usr/bin/env python3
"""
Independent triangular-face validator for the archived N=10 dataset.

This module intentionally does NOT import src/geometry.py and does not use the
legacy "no other line crosses the interior" predicate. Instead, it reconstructs
the combinatorial arrangement of the lines.

A triple (i, j, k) bounds a triangular face iff the two relevant intersections
are consecutive along each of the three lines i, j and k.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
from itertools import combinations
from typing import List, Optional, Sequence, Tuple

Line = Tuple[float, float, float]
Point = Tuple[float, float]


def normalize_line(line: Sequence[float]) -> Line:
    a, b, c = map(float, line)
    norm = math.hypot(a, b)
    if norm == 0.0:
        raise ValueError("invalid line with zero normal")
    return a / norm, b / norm, c / norm


def intersection(l1: Line, l2: Line, parallel_eps: float = 1e-12) -> Tuple[Optional[Point], float]:
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    det = a1 * b2 - b1 * a2
    if abs(det) <= parallel_eps:
        return None, abs(det)
    x = (b1 * c2 - c1 * b2) / det
    y = (c1 * a2 - a1 * c2) / det
    return (x, y), abs(det)


def count_triangular_faces(raw_lines: Sequence[Sequence[float]]) -> Tuple[int, float, float]:
    lines = [normalize_line(line) for line in raw_lines]
    n = len(lines)
    points: List[List[Optional[Point]]] = [[None] * n for _ in range(n)]
    min_abs_det = math.inf

    for i, j in combinations(range(n), 2):
        point, abs_det = intersection(lines[i], lines[j])
        min_abs_det = min(min_abs_det, abs_det)
        if point is None:
            raise ValueError(f"parallel or numerically parallel lines: {i}, {j}")
        points[i][j] = points[j][i] = point

    rank: List[dict[int, int]] = [dict() for _ in range(n)]
    min_adjacent_gap = math.inf

    for i, (a, b, _c) in enumerate(lines):
        ordered = []
        for j in range(n):
            if i == j:
                continue
            point = points[i][j]
            assert point is not None
            x, y = point
            t = x * b - y * a
            ordered.append((t, j))

        ordered.sort()
        for pos, (_t, other) in enumerate(ordered):
            rank[i][other] = pos

        for (t1, _), (t2, _) in zip(ordered, ordered[1:]):
            min_adjacent_gap = min(min_adjacent_gap, abs(t2 - t1))

    faces = 0
    for i, j, k in combinations(range(n), 3):
        if (
            abs(rank[i][j] - rank[i][k]) == 1
            and abs(rank[j][i] - rank[j][k]) == 1
            and abs(rank[k][i] - rank[k][j]) == 1
        ):
            faces += 1

    return faces, min_abs_det, min_adjacent_gap


def official_solution_paths() -> List[str]:
    rx = re.compile(r"^variant\d.*\.json$")
    paths = [
        path
        for path in glob.glob(os.path.join("solutions", "variant*.json"))
        if rx.match(os.path.basename(path))
    ]
    return sorted(paths)


def validate_file(path: str) -> Tuple[bool, int, Optional[int], float, float]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    faces, min_abs_det, min_gap = count_triangular_faces(data["lines"])
    declared = data.get("score")
    ok = declared is None or int(declared) == faces
    return ok, faces, declared, min_abs_det, min_gap


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Independent arrangement-face validator")
    parser.add_argument("paths", nargs="*", help="JSON configurations to validate")
    parser.add_argument("--all", action="store_true",
                        help="validate the 72 official solutions/variant<index>*.json files")
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.all:
        paths.extend(official_solution_paths())
    if not paths:
        parser.error("provide one or more JSON paths, or use --all")
    paths = list(dict.fromkeys(paths))

    failures = 0
    global_min_det = math.inf
    global_min_gap = math.inf
    min_gap_file = None

    for path in paths:
        try:
            ok, faces, declared, min_det, min_gap = validate_file(path)
            global_min_det = min(global_min_det, min_det)
            if min_gap < global_min_gap:
                global_min_gap = min_gap
                min_gap_file = path
            status = "OK" if ok else "MISMATCH"
            print(
                f"{status:8} {path}: faces={faces}, declared={declared}, "
                f"min|det|={min_det:.6g}, min_adjacent_gap={min_gap:.6g}"
            )
            if not ok:
                failures += 1
        except Exception as exc:
            failures += 1
            print(f"ERROR    {path}: {exc}", file=sys.stderr)

    print()
    print(f"validated files: {len(paths)}")
    print(f"failures:        {failures}")
    if math.isfinite(global_min_det):
        print(f"min |det|:       {global_min_det:.6g}")
    if math.isfinite(global_min_gap):
        print(f"min adj. gap:    {global_min_gap:.6g} ({min_gap_file})")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
