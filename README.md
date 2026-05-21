# 🎮 Steam Games Search Engine

An advanced information retrieval system for Steam games with AI-powered semantic search capabilities.

## Features

- **🔍 Three Search Modes**
  - **Keyword Search**: Traditional BM25-based text matching via Apache Solr
  - **Semantic Search**: AI-powered understanding using transformer embeddings
  - **Hybrid Search**: Intelligent combination of both approaches for optimal results

- **⚡ High Performance**
  - Fast keyword search (~10-50ms)
  - Efficient semantic search (~50-200ms)
  - Real-time results with score visualization

- **📊 Evaluation Framework**
  - TREC evaluation tools included
  - Support for qrels and information needs
  - Precision-recall curve generation

## Project Structure

```
PRI/
├── app.py                          # Main Flask web application
├── requirements-frontend.txt       # Python dependencies
├── docker-compose.yml             # Docker configuration for Solr
├── schema.json                    # Solr schema definition
│
├── semantic_search/               # 🧠 Semantic search package
│   ├── __init__.py               
│   ├── engine.py                 # Core semantic engine
│   ├── generate_embeddings.py    # Embedding generation
│   ├── test_setup.py             # Setup verification
│   └── embeddings/               # Stored embeddings
│
├── scripts/                       # 🛠️ Utility scripts
│   ├── compare_modes.py          # Compare search modes
│   ├── quick_start.py            # Automated setup
│   ├── plot_pr.py                # Precision-recall curves
│   ├── qrels2trec.py             # Format conversion
│   ├── query_solr.py             # Direct Solr queries
│   └── solr2trec.py              # Results conversion
│
├── data/                          # 📁 Data files
│   ├── processing/               # Data processing scripts
│   ├── games_cleaned.json        # Cleaned game dataset
│   └── games_cleaned.csv         # CSV version
│
├── config/                        # ⚙️ Configuration
│   ├── information_needs.txt     
│   ├── qrels/                    # Relevance judgments
│   └── queries/                  # Query definitions
│
├── docs/                          # 📚 Documentation
│   ├── SEMANTIC_SEARCH.md        # Complete semantic search guide
│   └── SETUP_CHECKLIST.md        # Setup verification
│
├── static/                        # 🎨 Web assets
│   ├── script.js                 
│   └── style.css                 
│
├── templates/                     # 🌐 HTML templates
│   └── index.html               
│
└── trec_eval/                     # 📊 Evaluation tools
```

## Quick Start

### Prerequisites

- Python 3.7+
- Docker (for Solr)
- 500MB free disk space

### 1. Install Dependencies

```bash
pip install -r requirements-frontend.txt
```

### 2. Start Solr

```bash
docker-compose up -d
```

Wait for Solr to start (~10 seconds), then apply schema:

```bash
curl -X POST -H 'Content-type:application/json' \
  --data-binary @schema.json \
  http://localhost:8983/solr/steam_games/schema
```

### 3. Index Data

```bash
# Post JSON data to Solr
curl -X POST -H 'Content-Type: application/json' \
  --data-binary @data/games_cleaned.json \
  'http://localhost:8983/solr/steam_games/update?commit=true'
```

### 4. Setup Semantic Search (Optional)

```bash
# Automated setup
python scripts/quick_start.py

# OR Manual
python semantic_search/test_setup.py
python semantic_search/generate_embeddings.py
```

### 5. Start Application

```bash
python app.py
```

Visit **http://localhost:5000**

## Usage

### Web Interface

1. **Select Search Mode**
   - Keyword: Traditional text matching
   - Semantic: AI-powered understanding
   - Hybrid: Combined approach ⭐ Recommended

2. **Enter Query**
   - Keyword: "multiplayer FPS shooter"
   - Semantic: "games about exploring mysterious alien worlds"
   - Hybrid: Works great with both!

3. **View Results**
   - Score badges show relevance
   - Color-coded by search mode
   - Detailed game information

### Compare Search Modes

```bash
python scripts/compare_modes.py
```

Analyzes differences between keyword, semantic, and hybrid search.

### Direct Solr Queries

```bash
python scripts/query_solr.py "your query here"
```

## Search Examples

### Keyword Search Best For:
- Exact titles: "Counter-Strike Global Offensive"
- Specific terms: "2023 RPG multiplayer"
- Metadata: "Early Access survival"

### Semantic Search Best For:
- Natural language: "games about exploring space"
- Concepts: "relaxing puzzle games"
- Descriptions: "emotional story-driven adventure"

### Hybrid Search Best For:
- General queries: "fantasy RPG with magic"
- Mixed intent: "competitive team shooter"
- Best overall results ⭐

## Data Processing

Process raw dataset:

```bash
# Clean dataset
python data/processing/clean_dataset.py

# Convert to JSON
python data/processing/csv_to_json.py

# Add categorical labels
python data/processing/add_labels.py
```

## Evaluation

### Run Evaluations

```bash
# Generate query results
python scripts/query_solr.py < config/queries/queries.txt > results.txt

# Convert to TREC format
python scripts/solr2trec.py results.txt > results.trec

# Evaluate with TREC tools
./trec_eval/trec_eval -m all_trec config/qrels/qrels.txt results.trec
```

### Plot Precision-Recall

```bash
python scripts/plot_pr.py results.trec config/qrels/qrels.txt
```

## Documentation

- **[Semantic Search Guide](docs/SEMANTIC_SEARCH.md)** - Complete guide for AI-powered search
- **[Setup Checklist](docs/SETUP_CHECKLIST.md)** - Verify your installation
- **[Frontend Docs](docs/FRONTEND_README.md)** - Web interface documentation

## Technology Stack

### Backend
- **Flask** - Web framework
- **Apache Solr** - Search engine
- **sentence-transformers** - Semantic embeddings
- **PyTorch** - Deep learning

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling
- **HTML5** - Semantic markup

### Evaluation
- **TREC eval** - Standard IR evaluation
- **Custom scripts** - Result analysis

## Configuration

### Solr Settings

Edit `schema.json` to customize:
- Field types and analyzers
- Boosting weights
- Vector search parameters

### Semantic Search

Edit `semantic_search/engine.py`:
- Model selection
- Embedding dimensions
- Similarity functions

### Hybrid Scoring

Edit `app.py` - `perform_hybrid_search()`:
```python
keyword_weight = 0.5  # Adjust balance (0-1)
```

## Performance

| Component | Typical Speed |
|-----------|---------------|
| Keyword Search | 10-50ms |
| Semantic Search | 50-200ms (after model load) |
| Hybrid Search | 100-300ms |
| First Semantic Query | 2-5s (model loading) |

## Development

### Project Setup for Development

```bash
# Clone repository
git clone <repository-url>
cd PRI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-frontend.txt

# Setup pre-commit hooks (if using)
pre-commit install
```

### Running Tests

```bash
# Test semantic search setup
python semantic_search/test_setup.py

# Test Solr connection
curl http://localhost:8983/solr/steam_games/select?q=*:*

# Compare search modes
python scripts/compare_modes.py
```

## Troubleshooting

### Solr Not Starting

```bash
docker ps  # Check if container is running
docker logs solr_pri  # View logs
```

### Semantic Search Errors

```bash
# Verify setup
python semantic_search/test_setup.py

# Check embeddings
ls semantic_search/embeddings/

# Regenerate if needed
python semantic_search/generate_embeddings.py
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements-frontend.txt --force-reinstall
```

## Contributing

This is an academic project for Information Retrieval coursework.

## License

Academic/Educational Use

## Acknowledgments

- **sentence-transformers** - For semantic embeddings
- **Apache Solr** - For search infrastructure
- **TREC** - For evaluation methodology

---

## Quick Commands Reference

```bash
# Start everything
docker-compose up -d
python app.py

# Setup semantic search
python scripts/quick_start.py

# Compare modes
python scripts/compare_modes.py

# Evaluate results
./trec_eval/trec_eval config/qrels/qrels.txt results.trec

# Stop Solr
docker-compose down
```

## Next Steps

1. ✅ Install dependencies
2. ✅ Start Solr and index data
3. ✅ Setup semantic search (optional)
4. ✅ Test search modes
5. ✅ Run evaluations
6. ✅ Analyze results

**Happy searching! 🚀**

For detailed semantic search documentation, see [docs/SEMANTIC_SEARCH.md](docs/SEMANTIC_SEARCH.md)
