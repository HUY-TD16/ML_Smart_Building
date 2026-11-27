#!/usr/bin/env python3
"""Quick benchmark runner to test and compare policies locally before Kaggle.

Modes:
  --mode smoke      : Run 1 day (288 steps) on 2 contrasting climates
                      (fairbanks_1 cold & phoenix_5 hot) for BOTH `transfer`
                      and `pid_water`, then print a side-by-side comparison.
  --mode 5climates  : Run full 30 days (8640 steps) on 5 climates of
                      building_train_1 and score against baseline_returns.json.
  --mode full       : Run full 30 days (8640 steps) on all 30 scenarios and
                      compute the official Leaderboard Score.

Usage (from starter-kit directory):
    python experiments/quick_benchmark.py --mode smoke
    python experiments/quick_benchmark.py --mode 5climates
    python experiments/quick_benchmark.py --mode full
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

STARTER_KIT_DIR = Path(__file__).resolve().parents[1]


def run_cmd(cmd: list[str]) -> int:
    print(f"\n>>> Running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(STARTER_KIT_DIR))
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=["smoke", "5climates", "full"],
        default="smoke",
        help="Benchmark mode (default: smoke)",
    )
    parser.add_argument(
        "--policy",
        default="transfer",
        help="Policy key to test (default: transfer)",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=None,
        help="Custom results directory",
    )
    args = parser.parse_args()

    py = sys.executable

    if args.mode == "smoke":
        res_dir = args.results_dir or Path("results/smoke_test")
        # Run both transfer and pid_water for 1 day (288 steps) on cold & hot climates
        rc = run_cmd(
            [
                py,
                "-m",
                "smart_buildings.evaluate",
                "--policies",
                args.policy,
                "pid_water",
                "--buildings",
                "building_train_1",
                "--weathers",
                "fairbanks_1",
                "phoenix_5",
                "--steps",
                "288",
                "--results-dir",
                str(res_dir),
            ]
        )
        if rc != 0:
            return rc
        return run_cmd(
            [
                py,
                "experiments/compare_runs.py",
                str(res_dir),
            ]
        )

    elif args.mode == "5climates":
        res_dir = args.results_dir or Path("results/bench_5climates")
        rc = run_cmd(
            [
                py,
                "-m",
                "smart_buildings.evaluate",
                "--policies",
                args.policy,
                "--buildings",
                "building_train_1",
                "--steps",
                "8640",
                "--results-dir",
                str(res_dir),
            ]
        )
        if rc != 0:
            return rc
        run_cmd([py, "experiments/compare_runs.py", str(res_dir)])
        return run_cmd(
            [
                py,
                "score_leaderboard.py",
                str(res_dir),
                "--policy",
                args.policy,
            ]
        )

    else:  # full
        res_dir = args.results_dir or Path(f"results/{args.policy}_full")
        rc = run_cmd(
            [
                py,
                "-m",
                "smart_buildings.evaluate",
                "--policies",
                args.policy,
                "--steps",
                "8640",
                "--results-dir",
                str(res_dir),
            ]
        )
        if rc != 0:
            return rc
        run_cmd([py, "experiments/compare_runs.py", str(res_dir)])
        return run_cmd(
            [
                py,
                "score_leaderboard.py",
                str(res_dir),
                "--policy",
                args.policy,
                "--expect",
                "30",
            ]
        )


if __name__ == "__main__":
    raise SystemExit(main())
