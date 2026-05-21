#!/usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import glob


def qrels_to_trec(qrels: Path, query_id_override=None) -> None:
    """
    Converts qrels (query relevance judgments) to TREC evaluation format.

    Arguments:
    - qrels: Path to qrels directory or single file.
    - query_id_override: If specified, use this query ID for all entries.
    """
    
    # Support both directory and single file
    if qrels.is_file():
        qrel_files = [qrels]
    else:
        qrel_files = [Path(f) for f in glob.glob(qrels.joinpath("*.txt").as_posix())]
    
    seen_docs = set()  # Track seen docs to avoid duplicates when using query_id_override
    
    for qrel_file in qrel_files:
        with open(qrel_file) as f:
            qrels_data = f.readlines()

        # Use override or filename as query ID
        query_id = query_id_override if query_id_override is not None else int(qrel_file.stem)

        for line in qrels_data:
            doc_id = line.strip()
            if not doc_id:
                continue
            # Avoid duplicates when merging multiple files with same query_id
            key = (query_id, doc_id)
            if key not in seen_docs:
                seen_docs.add(key)
                print(f"{query_id} 0 {doc_id} 1")


if __name__ == "__main__":
    """
    Read qrels from file and output them in TREC format.
    """
    parser = ArgumentParser(description="Convert QRELs to TREC format")

    parser.add_argument(
        "--qrels",
        type=Path,
        default="config/qrels/",
        help="Path to QREL directory or single file.",
    )
    parser.add_argument(
        "--query-id",
        type=int,
        default=None,
        help="Override query ID for all entries (default: use filename as query ID).",
    )

    args = parser.parse_args()

    qrels_to_trec(args.qrels, args.query_id)

