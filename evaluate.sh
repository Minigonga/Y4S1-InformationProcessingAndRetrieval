#!/usr/bin/env bash
set -euo pipefail

# Usage: ./evaluate.sh <queries_dir> <qrels_dir> <collection>

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <queries_dir> <qrels_dir> <collection>" >&2
    exit 1
fi

QUERIES_DIR="$1"
QRELS_DIR="$2"
COLLECTION="$3"

# Ensure output folder exists
mkdir -p "$QUERIES_DIR"

RESULTS_DIR="$QUERIES_DIR/metrics"
mkdir -p "$RESULTS_DIR"

# Intermediate files
QRELS_TREC="qrels_trec.txt"
RESULTS_TREC="$RESULTS_DIR/results_trec.txt"

# Output files
METRICS_FILE="$RESULTS_DIR/trec_metrics.txt"
PR_CURVE_FILE="$RESULTS_DIR/pr_curve.png"

echo "Converting qrels to TREC format..."
# Only numeric qrel files will be processed
./scripts/qrels2trec.py --qrels "$QRELS_DIR" > "$QRELS_TREC"

echo "Querying Solr and converting results to TREC format..."
./scripts/query_solr.py \
    --queries "$QUERIES_DIR" \
    --collection "$COLLECTION" \
| ./scripts/solr2trec.py > "$RESULTS_TREC"

echo "Running trec_eval and saving metrics to $METRICS_FILE..."
./trec_eval/trec_eval \
    -q -m num_rel_ret -m num_ret -m recip_rank \
    "$QRELS_TREC" "$RESULTS_TREC" > "$METRICS_FILE"


rm -f qrels_trec.txt results_trec.txt


echo "Evaluation complete!"
