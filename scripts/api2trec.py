#!/usr/bin/env python3
"""Convert semantic or hybrid API results into TREC evaluation format."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, Iterable, List
import sys


def iter_queries(payload: Dict[str, Any]) -> Iterable[tuple[int, Dict[str, Any]]]:
    """Yield (query_id, entry) pairs sorted by query id."""
    for key in sorted(payload.keys(), key=lambda value: int(value)):
        yield int(key), payload[key]


def resolve_score(doc: Dict[str, Any], mode: str, score_field: str | None) -> float:
    """Pick the appropriate numeric score for a document."""
    fields: List[str]

    if score_field:
        fields = [score_field]
    elif mode == "semantic":
        fields = ["semantic_score", "score"]
    elif mode == "hybrid":
        fields = ["hybrid_score", "semantic_score", "score"]
    else:
        fields = ["score"]

    for name in fields:
        value = doc.get(name)
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def convert(payload: Dict[str, Any], mode: str, run_id: str, score_field: str | None) -> None:
    """Print results in TREC format."""
    for query_id, entry in iter_queries(payload):
        docs = entry.get("results", [])
        for rank, doc in enumerate(docs, start=1):
            doc_id = doc.get("id")
            if not doc_id:
                continue
            score = resolve_score(doc, mode, score_field)
            print(f"{query_id} Q0 {doc_id} {rank} {score} {run_id}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert API results to TREC format")
    parser.add_argument(
        "--mode",
        choices=["keyword", "semantic", "hybrid"],
        default="semantic",
        help="Search mode used to fetch the results",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="semantic_run",
        help="Identifier for the evaluation run",
    )
    parser.add_argument(
        "--score-field",
        type=str,
        default=None,
        help="Explicit field name to use for scores (overrides default mode mapping)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        arguments = parse_args(sys.argv[1:])
        payload = json.load(sys.stdin)
        convert(payload, arguments.mode, arguments.run_id, arguments.score_field)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON input ({exc})", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
