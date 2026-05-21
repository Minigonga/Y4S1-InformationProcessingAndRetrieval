#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
import glob

import requests


def fetch_solr_results(query_file, solr_uri, collection):
    """
    Fetch search results from a Solr instance based on the query parameters.

    Arguments:
    - query_file: Path to the JSON file containing Solr query parameters.
    - solr_uri: URI of the Solr instance (e.g., http://localhost:8983/solr).
    - collection: Solr collection name from which results will be fetched.

    Output:
    - Prints the JSON search results to STDOUT.
    """

    # Load the query parameters from the JSON file
    try:
        query_params = json.load(open(query_file))
    except FileNotFoundError:
        print(f"Error: Query file {query_file} not found.")
        sys.exit(1)

    # Construct the Solr request URL
    uri = f"{solr_uri}/{collection}/select"

    try:
        # Send the POST request to Solr
        response = requests.post(uri, json=query_params)
        response.raise_for_status()  # Raise error if the request failed
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        sys.exit(1)

    # Fetch and print the results as JSON
    return response.json()


def main(query_path: Path, solr_uri, collection, query_id_override=None):

    results = {}

    # Support both single file and directory of files
    if query_path.is_file():
        # Single file: use override or filename stem as query ID
        query_id = query_id_override if query_id_override is not None else int(query_path.stem)
        results[query_id] = fetch_solr_results(
            query_path, solr_uri, collection
        )
    else:
        # Directory: process all JSON files
        for query_file in glob.glob(query_path.joinpath("*.json").as_posix()):
            filename = Path(query_file).stem
            query_id = query_id_override if query_id_override is not None else int(filename)
            results[query_id] = fetch_solr_results(
                query_file, solr_uri, collection
            )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    # Set up argument parsing for the command-line interface
    parser = argparse.ArgumentParser(
        description="Fetch search results from Solr and output them in JSON format."
    )

    parser.add_argument(
        "--queries",
        type=Path,
        required=True,
        help="Path to a JSON query file or directory containing JSON query files",
    )
    parser.add_argument(
        "--uri",
        type=str,
        default="http://localhost:8983/solr",
        help="The URI of the Solr instance (default: http://localhost:8983/solr).",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="courses",
        help="Name of the Solr collection to query (default: 'courses').",
    )
    parser.add_argument(
        "--query-id",
        type=int,
        default=None,
        help="Override query ID (default: use filename as query ID).",
    )

    args = parser.parse_args()

    main(args.queries, args.uri, args.collection, args.query_id)
