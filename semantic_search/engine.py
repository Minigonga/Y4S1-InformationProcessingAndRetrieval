#!/usr/bin/env python3
"""
Semantic Search Module
Provides functionality for generating embeddings and performing semantic similarity search
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import json
import os


class SemanticSearchEngine:
    """
    Handles semantic search using sentence embeddings.
    Uses a pre-trained transformer model to encode text into dense vectors.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic search engine
        
        Args:
            model_name: Name of the sentence-transformers model to use.
                       'all-MiniLM-L6-v2' is a good balance of speed and quality (384 dimensions)
                       'all-mpnet-base-v2' is more accurate but slower (768 dimensions)
        """
        print(f"Loading semantic search model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.embedding_dim}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode a single text into a dense vector embedding
        
        Args:
            text: The text to encode
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        if not text or not isinstance(text, str):
            return np.zeros(self.embedding_dim)
        
        embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
        return embedding
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Encode multiple texts into embeddings efficiently
        
        Args:
            texts: List of texts to encode
            batch_size: Number of texts to process at once
            
        Returns:
            numpy array of shape (n_texts, embedding_dim)
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts, 
            convert_to_numpy=True,
            batch_size=batch_size,
            show_progress_bar=True
        )
        return embeddings
    
    def prepare_game_text(self, game: Dict[str, Any]) -> str:
        """
        Create a comprehensive text representation of a game for embedding
        
        Args:
            game: Dictionary containing game information
            
        Returns:
            Combined text suitable for semantic embedding
        """
        parts = []
        
        # Title is most important
        if game.get('title'):
            parts.append(f"Title: {game['title']}")
        
        # Description/about
        if game.get('about_the_game'):
            # Truncate long descriptions to avoid overwhelming the embedding
            about = game['about_the_game']
            if len(about) > 1000:
                about = about[:1000] + "..."
            parts.append(f"Description: {about}")
        
        # Genres
        if game.get('genres'):
            if isinstance(game['genres'], list):
                parts.append(f"Genres: {', '.join(game['genres'])}")
            else:
                parts.append(f"Genres: {game['genres']}")
        
        # Categories
        if game.get('categories'):
            if isinstance(game['categories'], list):
                parts.append(f"Categories: {', '.join(game['categories'])}")
            else:
                parts.append(f"Categories: {game['categories']}")
        
        # Tags
        if game.get('tags'):
            if isinstance(game['tags'], list):
                # Limit to top 10 tags to avoid too much noise
                tags = game['tags'][:10] if len(game['tags']) > 10 else game['tags']
                parts.append(f"Tags: {', '.join(tags)}")
            else:
                parts.append(f"Tags: {game['tags']}")
        
        # Developers
        if game.get('developers'):
            if isinstance(game['developers'], list):
                parts.append(f"Developers: {', '.join(game['developers'])}")
            else:
                parts.append(f"Developers: {game['developers']}")
        
        return " | ".join(parts)
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1, vec2: Embedding vectors
            
        Returns:
            Similarity score between -1 and 1 (typically 0 to 1 for these embeddings)
        """
        if vec1.size == 0 or vec2.size == 0:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def find_similar(self, query_embedding: np.ndarray, 
                    candidate_embeddings: np.ndarray,
                    top_k: int = 10) -> List[tuple]:
        """
        Find most similar items to a query embedding
        
        Args:
            query_embedding: The query vector (embedding_dim,)
            candidate_embeddings: Matrix of candidate vectors (n_candidates, embedding_dim)
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by score descending
        """
        if candidate_embeddings.size == 0:
            return []
        
        # Normalize embeddings for efficient cosine similarity
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        candidates_norm = candidate_embeddings / (np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-10)
        
        # Compute similarities (matrix multiplication is much faster than individual comparisons)
        similarities = np.dot(candidates_norm, query_norm)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]
        return results
    
    def hybrid_score(self, keyword_score: float, semantic_score: float, 
                     keyword_weight: float = 0.5) -> float:
        """
        Combine keyword search score with semantic similarity score
        
        Args:
            keyword_score: Score from traditional keyword search (e.g., BM25)
            semantic_score: Cosine similarity score from semantic search
            keyword_weight: Weight for keyword score (0-1). Semantic weight is 1 - keyword_weight
            
        Returns:
            Combined hybrid score
        """
        semantic_weight = 1.0 - keyword_weight
        return keyword_weight * keyword_score + semantic_weight * semantic_score


def save_embeddings(embeddings: np.ndarray, ids: List[str], output_file: str):
    """
    Save embeddings to a file
    
    Args:
        embeddings: Array of embeddings (n_items, embedding_dim)
        ids: List of IDs corresponding to each embedding
        output_file: Path to output file
    """
    # Create directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    data = {
        'ids': ids,
        'embeddings': embeddings.tolist(),
        'dimension': embeddings.shape[1] if len(embeddings.shape) > 1 else embeddings.shape[0]
    }
    
    with open(output_file, 'w') as f:
        json.dump(data, f)
    
    print(f"Saved {len(ids)} embeddings to {output_file}")


def load_embeddings(input_file: str) -> tuple:
    """
    Load embeddings from a file
    
    Args:
        input_file: Path to input file
        
    Returns:
        Tuple of (embeddings array, ids list)
    """
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    embeddings = np.array(data['embeddings'])
    ids = data['ids']
    
    print(f"Loaded {len(ids)} embeddings from {input_file}")
    return embeddings, ids


if __name__ == '__main__':
    # Example usage
    engine = SemanticSearchEngine()
    
    # Test with some sample game data
    sample_games = [
        {
            'title': 'The Witcher 3',
            'about_the_game': 'Epic fantasy RPG with rich storytelling',
            'genres': ['RPG', 'Open World'],
            'tags': ['Story Rich', 'Fantasy', 'Magic']
        },
        {
            'title': 'Counter-Strike',
            'about_the_game': 'Competitive first-person shooter',
            'genres': ['Action', 'FPS'],
            'tags': ['Competitive', 'Multiplayer', 'Tactical']
        }
    ]
    
    # Generate embeddings
    texts = [engine.prepare_game_text(game) for game in sample_games]
    print("\nPrepared texts:")
    for i, text in enumerate(texts):
        print(f"{i+1}. {text[:100]}...")
    
    embeddings = engine.encode_batch(texts)
    print(f"\nGenerated embeddings shape: {embeddings.shape}")
    
    # Test similarity
    query = "fantasy role playing game"
    query_embedding = engine.encode_text(query)
    results = engine.find_similar(query_embedding, embeddings, top_k=2)
    
    print(f"\nQuery: '{query}'")
    print("Results:")
    for idx, score in results:
        print(f"  {idx+1}. {sample_games[idx]['title']} (score: {score:.4f})")
