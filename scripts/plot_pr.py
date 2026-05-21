#!/usr/bin/env python3

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

RECALL = np.arange(0.0, 1.1, 0.1)

def parse_eval_file(path: Path):
    metrics = {}
    with path.open() as f:
        for line in f:
            name, qid, value = line.split()
            # Take "all" for aggregate metrics
            if qid == "all":
                try:
                    metrics[name] = float(value)
                except ValueError:
                    metrics[name] = 0.0
    return metrics

def extract_curve(metrics):
    iprec = []
    for r in RECALL:
        # Try both formats: 0.00 (trec_eval default) and 0.0
        key_2dp = f"iprec_at_recall_{r:.2f}"
        key_1dp = f"iprec_at_recall_{r:.1f}"
        val = metrics.get(key_2dp, metrics.get(key_1dp, 0.0))
        iprec.append(val)
    auc = metrics.get("11pt_avg", 0.0)
    ap = metrics.get("map", 0.0)
    return np.array(iprec), auc, ap

def main():
    eval_files = {
        "Normal": Path("metrics/normal.eval"),
        "Boosted": Path("metrics/boosted.eval"),
        "Semantic": Path("metrics/semantic.eval"),
        "Hybrid": Path("metrics/hybrid.eval"),
    }

    plt.figure(figsize=(8, 6))

    for label, path in eval_files.items():
        if not path.exists():
            print(f"Warning: {path} does not exist, skipping {label}")
            continue
        metrics = parse_eval_file(path)
        precision, auc, ap = extract_curve(metrics)
        if precision.sum() == 0:
            print(f"Warning: {label} has all-zero precision, skipping curve")
            continue

        plt.plot(
            RECALL,
            precision,
            drawstyle="steps-post",
            linewidth=2,
            label=f"{label} (AP={ap:.3f}, AUC={auc:.3f})"
        )

    plt.title("Precision–Recall Curve Comparison")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("pr_auc_comparison.png")
    print("PR/AUC comparison saved as pr_auc_comparison.png")

if __name__ == "__main__":
    main()
