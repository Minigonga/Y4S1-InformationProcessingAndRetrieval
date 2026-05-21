#!/usr/bin/env python3
"""
Quick test script to verify semantic search setup
Run this after installing dependencies to check if everything works
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import torch
        print("✓ torch imported successfully")
        
        import numpy
        print("✓ numpy imported successfully")
        
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers imported successfully")
        
        import sklearn
        print("✓ scikit-learn imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements-frontend.txt")
        return False


def test_model_loading():
    """Test if the semantic search model can be loaded"""
    print("\nTesting model loading...")
    try:
        from sentence_transformers import SentenceTransformer
        
        print("Loading model (this may take a moment on first run)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print(f"✓ Model loaded successfully")
        print(f"  Embedding dimension: {model.get_sentence_embedding_dimension()}")
        
        return True, model
    except Exception as e:
        print(f"✗ Model loading error: {e}")
        return False, None


def test_embedding_generation(model):
    """Test if embeddings can be generated"""
    print("\nTesting embedding generation...")
    try:
        test_texts = [
            "Action packed first-person shooter",
            "Relaxing puzzle game with beautiful graphics",
            "Epic fantasy RPG adventure"
        ]
        
        print(f"Generating embeddings for {len(test_texts)} test texts...")
        embeddings = model.encode(test_texts, show_progress_bar=False)
        print(f"✓ Embeddings generated successfully")
        print(f"  Shape: {embeddings.shape}")
        
        # Test similarity calculation
        import numpy as np
        query = "competitive shooting game"
        query_emb = model.encode(query, show_progress_bar=False)
        
        # Calculate similarities
        similarities = []
        for i, emb in enumerate(embeddings):
            sim = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
            similarities.append((i, sim))
            print(f"  Similarity with text {i+1}: {sim:.4f}")
        
        best_match = max(similarities, key=lambda x: x[1])
        print(f"\n✓ Best match for '{query}': Text {best_match[0]+1}")
        print(f"  \"{test_texts[best_match[0]]}\"")
        
        return True
    except Exception as e:
        print(f"✗ Embedding generation error: {e}")
        return False


def test_semantic_search_module():
    """Test if our semantic_search.py module works"""
    print("\nTesting semantic_search module...")
    try:
        # Add parent directory to path to import semantic_search
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from semantic_search import SemanticSearchEngine
        
        print("Initializing SemanticSearchEngine...")
        engine = SemanticSearchEngine()
        print("✓ SemanticSearchEngine initialized")
        
        # Test game text preparation
        test_game = {
            'title': 'The Witcher 3',
            'about_the_game': 'Epic open-world RPG',
            'genres': ['RPG', 'Action'],
            'tags': ['Story Rich', 'Open World']
        }
        
        text = engine.prepare_game_text(test_game)
        print(f"✓ Game text preparation works")
        print(f"  Sample: {text[:100]}...")
        
        # Test encoding
        embedding = engine.encode_text(text)
        print(f"✓ Text encoding works")
        print(f"  Embedding shape: {embedding.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Semantic search module error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_data_files():
    """Check if required data files exist"""
    print("\nChecking data files...")
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    files_to_check = [
        (os.path.join(project_root, 'data', 'games.json'), 'Game data file'),
        (os.path.join(project_root, 'schema.json'), 'Solr schema file'),
    ]
    
    optional_files = [
        (os.path.join(project_root, 'semantic_search', 'embeddings', 'game_embeddings.json'), 
         'Pre-computed embeddings (run generate_embeddings.py to create)'),
    ]
    
    all_good = True
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} found ({size:,} bytes)")
        else:
            print(f"✗ {filename} not found - {description}")
            all_good = False
    
    print("\nOptional files:")
    for filename, description in optional_files:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} found ({size:,} bytes)")
        else:
            print(f"  {filename} not found - {description}")
    
    return all_good


def main():
    """Run all tests"""
    print("=" * 60)
    print("Semantic Search Setup Test")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Package imports", test_imports()))
    
    if not results[0][1]:
        print("\n❌ Cannot proceed without required packages")
        print("Install them with: pip install -r requirements-frontend.txt")
        sys.exit(1)
    
    # Test model loading
    success, model = test_model_loading()
    results.append(("Model loading", success))
    
    if not success:
        print("\n❌ Model loading failed")
        sys.exit(1)
    
    # Test embedding generation
    results.append(("Embedding generation", test_embedding_generation(model)))
    
    # Test semantic search module
    results.append(("Semantic search module", test_semantic_search_module()))
    
    # Check data files
    results.append(("Data files", check_data_files()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All tests passed!")
        print("\nNext steps:")
        print("1. Run 'python generate_embeddings.py' to create embeddings")
        print("2. Run 'python app.py' to start the web application")
        print("3. Open http://localhost:5000 and try semantic search!")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install -r requirements-frontend.txt")
        print("- Check if data files exist in the current directory")
        print("- Ensure you have internet connection for first-time model download")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
