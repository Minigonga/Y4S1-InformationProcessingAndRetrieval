#!/usr/bin/env bash
set -euo pipefail

# Usage: ./evaluate_separate.sh <queries_dir> <qrels_dir> <collection>

if [[ $# -lt 3 ]]; then
    echo "Usage: $0 <queries_dir> <qrels_dir> <collection>" >&2
    exit 1
fi

QUERIES_DIR="$1"
QRELS_DIR="$2"
COLLECTION="$3"

PYTHON_BIN="${PYTHON_BIN:-python3}"
SOLR_URI="http://localhost:8983/solr"
API_BASE="http://192.168.1.234:5000"
API_URL="${API_BASE%/}/search"
ROWS=10
TIMEOUT=60

TRECEVAL="./trec_eval/trec_eval"
RUNS_DIR="runs"
METRICS_DIR="metrics"

mkdir -p "$RUNS_DIR" "$METRICS_DIR"
QRELS_TREC="$METRICS_DIR/qrels_trec.txt"

# Convert qrels to TREC format
echo "Converting qrels to TREC format..."
"$PYTHON_BIN" ./scripts/qrels2trec.py --qrels "$QRELS_DIR" --query-id 1 > "$QRELS_TREC"

# -----------------------------
# NORMAL
# -----------------------------
echo "Running NORMAL..."
"$PYTHON_BIN" ./scripts/query_solr.py \
    --queries "$QUERIES_DIR/1.json" \
    --uri "$SOLR_URI" \
    --collection "$COLLECTION" \
    --query-id 1 \
| "$PYTHON_BIN" ./scripts/solr2trec.py --run-id normal > "$RUNS_DIR/normal.trec"

# -----------------------------
# BOOSTED
# -----------------------------
echo "Running BOOSTED..."
"$PYTHON_BIN" ./scripts/query_solr.py \
    --queries "$QUERIES_DIR/2.json" \
    --uri "$SOLR_URI" \
    --collection "$COLLECTION" \
    --query-id 1 \
| "$PYTHON_BIN" ./scripts/solr2trec.py --run-id boosted > "$RUNS_DIR/boosted.trec"

# -----------------------------
# SEMANTIC
# -----------------------------
echo "Running SEMANTIC..."
"$PYTHON_BIN" ./scripts/query_semantic.py \
    --queries "$QUERIES_DIR" \
    --mode semantic \
    --rows "$ROWS" \
    --api-url "$API_URL" \
    --timeout "$TIMEOUT" \
| "$PYTHON_BIN" ./scripts/api2trec.py --mode semantic --run-id semantic > "$RUNS_DIR/semantic.trec"

# -----------------------------
# HYBRID
# -----------------------------
echo "Running HYBRID..."
"$PYTHON_BIN" ./scripts/query_semantic.py \
    --queries "$QUERIES_DIR" \
    --mode hybrid \
    --rows "$ROWS" \
    --api-url "$API_URL" \
    --timeout "$TIMEOUT" \
| "$PYTHON_BIN" ./scripts/api2trec.py --mode hybrid --run-id hybrid > "$RUNS_DIR/hybrid.trec"

# -----------------------------
# Run trec_eval
# -----------------------------
echo "Running trec_eval..."
for RUN in normal boosted semantic hybrid; do
    echo "  Evaluating $RUN"
    "$TRECEVAL" \
        -m num_rel \
        -m num_ret \
        -m num_rel_ret \
        -m map \
        -m recip_rank \
        -m 11pt_avg \
        -m P.10 \
        -m iprec_at_recall \
        "$QRELS_TREC" "$RUNS_DIR/$RUN.trec" \
        > "$METRICS_DIR/$RUN.eval"
done

# -----------------------------
# Plot PR / AUC curves
# -----------------------------
echo "Plotting PR / AUC comparison..."
"$PYTHON_BIN" ./scripts/plot_pr.py

echo "Done! PR/AUC curves saved in pr_auc_comparison.png"
