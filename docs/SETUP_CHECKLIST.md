# ✅ Semantic Search Setup Checklist

Use this checklist to ensure everything is properly set up.

## Prerequisites

- [ ] Python 3.7 or higher installed
- [ ] `pip` package manager available
- [ ] At least 500MB free disk space
- [ ] Internet connection (for first-time model download)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements-frontend.txt
```

Expected packages:
- [ ] Flask==3.0.0
- [ ] flask-cors==4.0.0
- [ ] requests==2.31.0
- [ ] sentence-transformers==2.2.2
- [ ] torch==2.1.0
- [ ] numpy==1.24.3
- [ ] scikit-learn==1.3.0
- [ ] tqdm==4.66.1

**Verification:**
```bash
python -c "import torch, sentence_transformers; print('✓ All imports successful')"
```

### 2. Test Setup

```bash
python test_semantic_search.py
```

Expected results:
- [ ] ✓ Package imports
- [ ] ✓ Model loading
- [ ] ✓ Embedding generation
- [ ] ✓ Semantic search module
- [ ] ✓ Data files

### 3. Generate Embeddings

```bash
python generate_embeddings.py
```

Follow prompts:
1. Choose option **2** (Load from games_cleaned.json)
2. Wait for embedding generation (2-5 minutes)
3. Choose **n** for updating Solr (optional)

**Verification:**
- [ ] File `game_embeddings.json` created
- [ ] File size is reasonable (~1-5MB)

### 4. Start Application

```bash
python app.py
```

Expected output:
```
Loading semantic search engine...
Model loaded. Embedding dimension: 384
 * Running on http://127.0.0.1:5000
```

### 5. Test Web Interface

Open http://localhost:5000

- [ ] Page loads successfully
- [ ] Search mode dropdown visible
- [ ] Can switch between Keyword/Semantic/Hybrid
- [ ] Mode description updates when selecting

### 6. Test Each Search Mode

#### Keyword Search
Query: "Counter-Strike"
- [ ] Results returned
- [ ] Shows score badges
- [ ] Fast response (<100ms)

#### Semantic Search  
Query: "games about exploring space"
- [ ] Results returned (may differ from keyword)
- [ ] Shows similarity percentages
- [ ] Response within ~200ms after first query

#### Hybrid Search
Query: "relaxing puzzle games"
- [ ] Results returned
- [ ] Shows hybrid scores with breakdown
- [ ] Combines both approaches

## Troubleshooting

### Import Errors

**Error:** `Import "sentence_transformers" could not be resolved`

**Fix:**
```bash
pip install sentence-transformers
```

### Model Download Issues

**Error:** Download fails or times out

**Fix:**
1. Check internet connection
2. Try again (downloads resume)
3. Use proxy if needed:
   ```bash
   export HTTP_PROXY=your_proxy
   pip install sentence-transformers
   ```

### Memory Issues

**Error:** Out of memory during embedding generation

**Fix:**
1. Close other applications
2. Reduce batch size in `generate_embeddings.py`:
   ```python
   embeddings = engine.encode_batch(texts, batch_size=16)  # Default is 32
   ```

### Embeddings Not Available

**Error:** "Embeddings not available" when using semantic search

**Fix:**
```bash
python generate_embeddings.py
```

### Slow Performance

**Issue:** First semantic query takes 3-5 seconds

**Explanation:** This is normal - the model needs to load into memory. Subsequent queries will be much faster.

## File Checklist

After setup, verify these files exist:

### Required Files
- [ ] `semantic_search.py` - Core semantic engine
- [ ] `generate_embeddings.py` - Embedding generator
- [ ] `app.py` - Updated Flask app
- [ ] `requirements-frontend.txt` - Updated dependencies
- [ ] `schema.json` - Updated Solr schema
- [ ] `templates/index.html` - Updated UI
- [ ] `static/script.js` - Updated frontend
- [ ] `static/style.css` - Updated styles

### Generated Files (after running scripts)
- [ ] `game_embeddings.json` - Pre-computed embeddings

### Documentation Files
- [ ] `SEMANTIC_SEARCH_README.md` - Quick reference
- [ ] `SEMANTIC_SEARCH_GUIDE.md` - Comprehensive guide
- [ ] `SEMANTIC_SEARCH_IMPLEMENTATION.md` - Technical details
- [ ] `THIS_FILE.md` - Setup checklist

### Utility Scripts
- [ ] `test_semantic_search.py` - Setup verification
- [ ] `quick_start.py` - Automated setup
- [ ] `compare_search_modes.py` - Mode comparison tool

## Performance Benchmarks

After setup, you should see approximately:

| Metric | Expected Value |
|--------|---------------|
| First query (semantic) | 2-5 seconds |
| Subsequent queries (semantic) | 50-200ms |
| Keyword search | 10-50ms |
| Hybrid search | 100-300ms |
| Memory usage (idle) | ~200-300MB |
| Embedding file size (1k games) | ~1-2MB |

## Feature Checklist

Confirm these features work:

### Search Modes
- [ ] Can select Keyword mode
- [ ] Can select Semantic mode  
- [ ] Can select Hybrid mode
- [ ] Mode description updates

### Results Display
- [ ] Results show for all modes
- [ ] Score badges display correctly
- [ ] Keyword shows BM25 score
- [ ] Semantic shows similarity %
- [ ] Hybrid shows combined score + breakdown

### UI Elements
- [ ] Search box functional
- [ ] Results per page selector works
- [ ] Game cards display properly
- [ ] Images load (or placeholder shown)
- [ ] Genres/tags displayed

## Next Steps

Once everything is checked:

1. [ ] Test with your information needs
2. [ ] Compare results across modes
3. [ ] Collect metrics (precision, recall, etc.)
4. [ ] Document findings in your report
5. [ ] Consider tuning hybrid weights

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements-frontend.txt

# Test setup
python test_semantic_search.py

# Generate embeddings
python generate_embeddings.py

# Start application
python app.py

# Compare search modes (server must be running)
python compare_search_modes.py

# Quick start (automated)
python quick_start.py
```

## Support Resources

- **Detailed Guide**: See `SEMANTIC_SEARCH_GUIDE.md`
- **Implementation Details**: See `SEMANTIC_SEARCH_IMPLEMENTATION.md`
- **Quick Reference**: See `SEMANTIC_SEARCH_README.md`

## Verification Command

Run this to verify everything at once:

```bash
python test_semantic_search.py && echo "✅ Setup complete!"
```

---

**All checked? You're ready to go! 🚀**
