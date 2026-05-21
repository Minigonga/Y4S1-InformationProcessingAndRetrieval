#!/usr/bin/env python3
"""
Generate embeddings for all games in the dataset and store them in Solr
This script should be run after your Solr instance is up and populated with game data
"""

import json
import requests
import sys
import os
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from semantic_search import SemanticSearchEngine, save_embeddings


# Configuration
SOLR_URI = "http://localhost:8983/solr"
COLLECTION = "steam_games"
EMBEDDINGS_FILE = "embeddings/game_embeddings.json"


def fetch_all_games_from_solr():
    """Fetch all games from Solr"""
    print("Fetching games from Solr...")
    
    all_docs = []
    start = 0
    rows = 1000
    
    while True:
        try:
            response = requests.get(
                f"{SOLR_URI}/{COLLECTION}/select",
                params={
                    'q': '*:*',
                    'rows': rows,
                    'start': start,
                    'fl': 'id,title,about_the_game,genres,categories,tags,developers,age_rating_label,release_year_label,price_range_label,OS_label,playtime_label',
                    'wt': 'json'
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            docs = data['response']['docs']
            if not docs:
                break
            
            all_docs.extend(docs)
            num_found = data['response']['numFound']
            
            print(f"Fetched {len(all_docs)}/{num_found} games...")
            
            if len(all_docs) >= num_found:
                break
            
            start += rows
            
        except Exception as e:
            print(f"Error fetching games: {e}")
            sys.exit(1)
    
    print(f"Successfully fetched {len(all_docs)} games")
    return all_docs


def generate_and_store_embeddings(games, engine):
    """Generate embeddings for all games"""
    print(f"\nGenerating embeddings for {len(games)} games...")
    
    # Prepare texts
    texts = []
    ids = []
    
    for game in tqdm(games, desc="Preparing texts"):
        text = engine.prepare_game_text(game)
        texts.append(text)
        ids.append(game['id'])
    
    # Generate embeddings in batches
    print("\nEncoding texts to embeddings...")
    embeddings = engine.encode_batch(texts, batch_size=32)
    
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    # Save embeddings to file for later use
    save_embeddings(embeddings, ids, EMBEDDINGS_FILE)
    
    return embeddings, ids


def update_solr_with_embeddings(games, embeddings, ids):
    """
    Update Solr documents with their embedding vectors
    Note: This requires Solr 9+ with dense vector support
    """
    print("\nUpdating Solr documents with embeddings...")
    
    # Create a map of id to embedding
    id_to_embedding = {id_val: emb.tolist() for id_val, emb in zip(ids, embeddings)}
    
    # Prepare update documents
    update_docs = []
    for game in games:
        game_id = game['id']
        if game_id in id_to_embedding:
            update_docs.append({
                'id': game_id,
                'embedding_vector': {'set': id_to_embedding[game_id]}
            })
    
    # Send updates to Solr in batches
    batch_size = 100
    total_batches = (len(update_docs) + batch_size - 1) // batch_size
    
    for i in tqdm(range(0, len(update_docs), batch_size), desc="Updating Solr", total=total_batches):
        batch = update_docs[i:i+batch_size]
        
        try:
            response = requests.post(
                f"{SOLR_URI}/{COLLECTION}/update?commit=true",
                json=batch,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
        except Exception as e:
            print(f"\nError updating Solr batch {i//batch_size + 1}: {e}")
            print("Continuing with next batch...")
            continue
    
    print(f"Successfully updated {len(update_docs)} documents in Solr")


def load_games_from_json(json_file):
    """Load games from local JSON file instead of Solr"""
    print(f"Loading games from {json_file}...")
    
    # Look in parent directory for data file
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(parent_dir, 'data', json_file)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            games = json.load(f)
        
        print(f"Loaded {len(games)} games from JSON file")
        return games
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        sys.exit(1)


def main():
    """Main execution function"""
    print("=" * 60)
    print("Game Embeddings Generator")
    print("=" * 60)
    
    # Initialize semantic search engine
    engine = SemanticSearchEngine(model_name='all-MiniLM-L6-v2')
    
    # Choose data source
    print("\nSelect data source:")
    print("1. Fetch from Solr (requires Solr to be running)")
    print("2. Load from games.json file")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == '1':
        games = fetch_all_games_from_solr()
    elif choice == '2':
        games = load_games_from_json('../data/games.json')
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)
    
    if not games:
        print("No games found. Exiting.")
        sys.exit(1)
    
    # Generate embeddings
    embeddings, ids = generate_and_store_embeddings(games, engine)
    
    # Ask if user wants to update Solr
    update_solr = input("\nUpdate Solr with embeddings? (y/n): ").strip().lower()
    
    if update_solr == 'y':
        print("\nNote: This requires your Solr schema to have an 'embedding_vector' field.")
        print("Make sure you've updated your schema before proceeding.")
        proceed = input("Continue? (y/n): ").strip().lower()
        
        if proceed == 'y':
            update_solr_with_embeddings(games, embeddings, ids)
    
    print("\n" + "=" * 60)
    print("Done! Embeddings have been generated and saved.")
    print(f"Embeddings file: {EMBEDDINGS_FILE}")
    print("=" * 60)


if __name__ == '__main__':
    main()
