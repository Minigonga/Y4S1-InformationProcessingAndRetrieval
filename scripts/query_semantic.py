#!/usr/bin/env python3
"""Query the Flask search API to retrieve semantic or hybrid search results for evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
import glob
import sys

import requests
import os


# Use host.docker.internal for Docker, or check for WSL and use the Windows host IP
def get_default_api_url():
    # Check if running in WSL
    if os.path.exists('/proc/version'):
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    # WSL detected - use Windows host IP
                    try:
                        import subprocess
                        result = subprocess.run(
                            ['cat', '/etc/resolv.conf'],
                            capture_output=True, text=True
                        )
                        for line in result.stdout.split('\n'):
                            if 'nameserver' in line:
                                host_ip = line.split()[1]
                                return f"http://{host_ip}:5000/search"
                    except:
                        pass
        except:
            pass
    return "http://localhost:5000/search"


DEFAULT_API_URL = get_default_api_url()


def load_query_text(path: Path) -> str:
    """Extract the free-form query text from a JSON query definition."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Query file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc

    if isinstance(data, dict):
        if "query" in data and isinstance(data["query"], str):
            return data["query"].strip()
        if "q" in data and isinstance(data["q"], str):
            return data["q"].strip()

    raise RuntimeError(f"Could not find query text in {path}")


def fetch_results(
    api_url: str,
    query_text: str,
    mode: str,
    rows: int,
    timeout: float,
) -> List[Dict[str, Any]]:
    """Call the search API and return the result list for a query."""
    payload = {"query": query_text, "mode": mode, "rows": rows}
    response = requests.post(api_url, json=payload, timeout=timeout)
    response.raise_for_status()

    data = response.json()
    if not data.get("success"):
        error_detail = data.get("error", "Unknown API error")
        raise RuntimeError(f"API returned an error: {error_detail}")

    return data.get("results", [])


def main(args: argparse.Namespace) -> None:
    api_url = args.api_url.rstrip("/")
    query_dir = args.queries
    results: Dict[str, Dict[str, Any]] = {}

    pattern = query_dir.joinpath("*.json").as_posix()
    files = sorted(glob.glob(pattern))
    if not files:
        raise RuntimeError(f"No query JSON files found in {query_dir}")

    for filename in files:
        path = Path(filename)
        query_id = path.stem
        query_text = load_query_text(path)
        docs = fetch_results(api_url, query_text, args.mode, args.rows, args.timeout)

        results[str(int(query_id))] = {
            "query": query_text,
            "results": docs,
        }

    json.dump(results, sys.stdout, indent=2)
    sys.stdout.write("\n")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query the semantic search API")
    parser.add_argument(
        "--queries",
        type=Path,
        required=True,
        help="Directory with query JSON definitions",
    )
    parser.add_argument(
        "--mode",
        choices=["keyword", "semantic", "hybrid"],
        default="semantic",
        help="Search mode to request from the API",
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=10,
        help="Number of results to request per query",
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default=DEFAULT_API_URL,
        help="Full API endpoint for the /search route",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout in seconds",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    try:
        arguments = parse_args(sys.argv[1:])
        main(arguments)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
