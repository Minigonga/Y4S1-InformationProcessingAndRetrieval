#!/usr/bin/env python3
"""
Compare search modes side-by-side
Useful for understanding the differences between keyword, semantic, and hybrid search
"""

import requests
import json
from typing import List, Dict

# Configuration
API_URL = "http://localhost:5000/search"

def search(query: str, mode: str, rows: int = 5) -> Dict:
    """Perform a search with the specified mode"""
    try:
        response = requests.post(
            API_URL,
            json={'query': query, 'mode': mode, 'rows': rows},
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {'success': False, 'error': str(e)}

def print_results(mode: str, data: Dict, max_display: int = 3):
    """Print search results in a formatted way"""
    if not data.get('success'):
        print(f"  ❌ Error: {data.get('error', 'Unknown error')}")
        return
    
    results = data.get('results', [])
    num_found = data.get('numFound', 0)
    qtime = data.get('qtime', 0)
    
    print(f"  📊 Found {num_found} results in {qtime}ms")
    print()
    
    for i, doc in enumerate(results[:max_display], 1):
        title = doc.get('title', 'Untitled')
        
        # Get appropriate score
        if mode == 'keyword':
            score = doc.get('score', 0)
            score_str = f"Score: {score:.2f}"
        elif mode == 'semantic':
            score = doc.get('semantic_score', 0)
            score_str = f"Similarity: {score*100:.1f}%"
        else:  # hybrid
            hybrid = doc.get('hybrid_score', 0)
            keyword = doc.get('keyword_score', 0)
            semantic = doc.get('semantic_score', 0)
            score_str = f"Hybrid: {hybrid*100:.1f}% (KW:{keyword*100:.0f}% + Sem:{semantic*100:.0f}%)"
        
        print(f"  {i}. {title}")
        print(f"     {score_str}")
        
        # Show some metadata
        genres = doc.get('genres', [])
        if genres:
            if isinstance(genres, list):
                print(f"     Genres: {', '.join(genres[:3])}")
            else:
                print(f"     Genres: {genres}")
        print()

def compare_modes(query: str, rows: int = 5):
    """Compare all three search modes for a given query"""
    print("=" * 80)
    print(f"Query: \"{query}\"")
    print("=" * 80)
    
    modes = ['keyword', 'semantic', 'hybrid']
    mode_names = {
        'keyword': '🔤 KEYWORD SEARCH',
        'semantic': '🧠 SEMANTIC SEARCH',
        'hybrid': '⚡ HYBRID SEARCH'
    }
    
    results = {}
    for mode in modes:
        print(f"\n{mode_names[mode]}")
        print("-" * 80)
        data = search(query, mode, rows)
        results[mode] = data
        print_results(mode, data)
    
    # Show unique games in each approach
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    if all(r.get('success') for r in results.values()):
        keyword_ids = {doc['id'] for doc in results['keyword'].get('results', [])[:rows]}
        semantic_ids = {doc['id'] for doc in results['semantic'].get('results', [])[:rows]}
        hybrid_ids = {doc['id'] for doc in results['hybrid'].get('results', [])[:rows]}
        
        only_keyword = keyword_ids - semantic_ids
        only_semantic = semantic_ids - keyword_ids
        both = keyword_ids & semantic_ids
        
        print(f"\n📈 Overlap Analysis (top {rows} results):")
        print(f"  • In both keyword & semantic: {len(both)} games")
        print(f"  • Only in keyword: {len(only_keyword)} games")
        print(f"  • Only in semantic: {len(only_semantic)} games")
        print(f"  • Hybrid captures: {len(hybrid_ids)} games")
        
        if only_keyword:
            print(f"\n  💡 Keyword found but semantic missed:")
            for doc in results['keyword'].get('results', []):
                if doc['id'] in only_keyword:
                    print(f"     - {doc.get('title')}")
        
        if only_semantic:
            print(f"\n  💡 Semantic found but keyword missed:")
            for doc in results['semantic'].get('results', []):
                if doc['id'] in only_semantic:
                    print(f"     - {doc.get('title')}")
    
    print("\n" + "=" * 80)

def main():
    """Main comparison function"""
    print("\n🔍 Search Mode Comparison Tool")
    print("=" * 80)
    
    # Check if server is running
    try:
        requests.get("http://localhost:5000", timeout=2)
    except:
        print("❌ Error: Server not running!")
        print("Please start the server with: python app.py")
        return
    
    print("✓ Server is running\n")
    
    # Predefined comparison queries
    sample_queries = [
        "games about exploring space",
        "relaxing puzzle games",
        "competitive multiplayer shooter",
        "medieval fantasy RPG",
        "zombie survival horror"
    ]
    
    print("Sample queries for comparison:")
    for i, q in enumerate(sample_queries, 1):
        print(f"  {i}. {q}")
    print(f"  {len(sample_queries) + 1}. Enter custom query")
    print()
    
    choice = input("Select a query (1-6) or press Enter to skip: ").strip()
    
    if choice:
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(sample_queries):
                query = sample_queries[choice_num - 1]
            elif choice_num == len(sample_queries) + 1:
                query = input("\nEnter your query: ").strip()
            else:
                print("Invalid choice")
                return
        except ValueError:
            print("Invalid input")
            return
    else:
        print("\nRunning comparison with sample query...")
        query = sample_queries[0]
    
    if not query:
        print("No query provided")
        return
    
    # Run comparison
    compare_modes(query)
    
    # Ask if user wants to try another
    print()
    another = input("Try another query? (y/n): ").strip().lower()
    if another == 'y':
        while True:
            query = input("\nEnter query (or 'quit' to exit): ").strip()
            if query.lower() == 'quit':
                break
            if query:
                compare_modes(query)
                print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nComparison cancelled.")
