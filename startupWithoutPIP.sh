# --- Exit on error ---
set -e

# --- Remove old container if exists ---
docker rm -f meic_solr 2>/dev/null || true

# --- Run Solr container ---
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
     --data-binary @games.json \
     "http://localhost:8983/solr/steam_games/update?commit=true"

echo "Solr core is ready with schema applied and data indexed."
