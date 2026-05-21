# --- Exit on error ---
set -e

# --- Install Python dependencies ---
pip install Flask>=3.0.0 \
            flask-cors>=4.0.0 \
            requests>=2.31.0 \
            sentence-transformers>=2.7.0 \
            torch>=2.0.0 \
            numpy>=1.26.0 \
            scikit-learn>=1.3.0 \
            tqdm>=4.66.1

# --- Remove old container if exists ---
docker rm -f meic_solr 2>/dev/null || true

# --- Run Solr container with CORS enabled ---
docker run -d -p 8983:8983 --name meic_solr -v "${PWD}:/data" solr:9

# --- Wait for Solr to start ---
echo "Waiting for Solr to start..."
sleep 15  # adjust if needed

# --- Create a new core ---
docker exec meic_solr solr create -c steam_games -n solrconf

# --- Upload schema BEFORE data ---
echo "Uploading schema..."
curl -X POST -H "Content-Type: application/json" \
     --data-binary @schema.json \
     "http://localhost:8983/solr/steam_games/schema"

# --- Upload dataset ---
echo "Uploading JSON data..."
curl -X POST -H "Content-Type: application/json" \
     --data-binary @data/games.json \
     "http://localhost:8983/solr/steam_games/update?commit=true"

echo "Solr core is ready with schema applied and data indexed."

# --- Direct Solr Connection (Keyword Search Only) ---
echo ""
echo "You can query Solr directly from the browser for keyword search without Python."
echo "Open 'index-solr-direct.html' in your browser to test direct Solr queries."
