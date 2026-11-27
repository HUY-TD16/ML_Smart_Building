#!/usr/bin/env python3
"""Compare evaluated policies with detailed breakdown of Comfort, Energy, and Carbon.

Reads `summary.json` files inside a results directory and prints:
1. Per-scenario and overall Mean Step Loss (|total_reward| / steps) — lower is better.
2. Component breakdown:
   - Comfort / Productivity Regret (weight 0.6)
   - Energy Cost (weight 0.2)
   - Carbon Emission (weight 0.2)

Usage (from starter-kit directory):
    python experiments/compare_runs.py results/smoke_test
    python experiments/compare_runs.py smart_buildings/results
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_summaries(root: Path) -> dict[str, dict[str, dict[str, Any]]]:
    """Return {scenario_key: {policy_name: summary_dict}}."""
    tree: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for f in sorted(root.glob("building_*/*/*/summary.json")):
        scenario = f"{f.parts[-4]}/{f.parts[-3]}"
        policy = f.parts[-2]
        with open(f, encoding="utf-8") as fp:
            tree[scenario][policy] = json.load(fp)
    return dict(tree)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "results_dir",
        type=Path,
        nargs="?",
        default=Path("smart_buildings/results"),
        help="Path to evaluation results directory",
    )
    args = parser.parse_args()

    tree = load_summaries(args.results_dir)
    if not tree:
        print(f"No summary.json files found under: {args.results_dir}")
        return 1

    policies = sorted({p for scen_dict in tree.values() for p in scen_dict.keys()})
    scenarios = sorted(tree.keys())

    print("\n" + "=" * 88)
    print(f"DETAILED PERFORMANCE COMPARISON ({args.results_dir}) — LOWER SCORE IS BETTER")
    print("=" * 88)
    header = (
        f"{'Scenario':<30} | {'Policy':<14} | {'Steps':>5} | "
        f"{'Score (Loss/step)':>17} | {'Comfort':>8} | {'Energy':>8} | {'Carbon':>8}"
    )
    print(header)
    print("-" * len(header))

    agg: dict[str, list[tuple[float, float, float, float]]] = defaultdict(list)

    for scen in scenarios:
        for pol in policies:
            s = tree[scen].get(pol)
            if not s:
                continue
            steps = max(int(s.get("total_steps", 1)), 1)
            loss_per_step = abs(float(s.get("total_reward", 0.0))) / steps
            comfort = float(s.get("total_normalized_productivity_regret", 0.0)) / steps
            energy = float(s.get("total_normalized_energy_cost", 0.0)) / steps
            carbon = float(s.get("total_normalized_carbon_emission", 0.0)) / steps

            agg[pol].append((loss_per_step, comfort, energy, carbon))
            print(
                f"{scen:<30} | {pol:<14} | {steps:>5d} | "
                f"{loss_per_step:>17.5f} | {comfort:>8.4f} | {energy:>8.4f} | {carbon:>8.4f}"
            )
        print("-" * len(header))

    print("\n=== OVERALL AVERAGE ACROSS EVALUATED SCENARIOS (LOWER IS BETTER) ===")
    print(
        f"{'Policy':<16} | {'Scenarios':>9} | {'Mean Score':>12} | "
        f"{'Comfort':>10} | {'Energy':>10} | {'Carbon':>10}"
    )
    print("-" * 78)
    for pol in sorted(agg.keys(), key=lambda p: sum(x[0] for x in agg[p]) / len(agg[p])):
        rows = agg[pol]
        n = len(rows)
        m_score = sum(x[0] for x in rows) / n
        m_comf = sum(x[1] for x in rows) / n
        m_ener = sum(x[2] for x in rows) / n
        m_carb = sum(x[3] for x in rows) / n
        print(
            f"{pol:<16} | {n:>9d} | {m_score:>12.5f} | "
            f"{m_comf:>10.5f} | {m_ener:>10.5f} | {m_carb:>10.5f}"
        )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
