#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from semantic_search import SemanticSearchEngine, load_embeddings

app = Flask(__name__)
CORS(app)

# Solr configuration
SOLR_URI = "http://localhost:8983/solr"
COLLECTION = "steam_games"

# Initialize semantic search engine (lazy loading)
semantic_engine = None
game_embeddings = None
game_ids = None

def get_semantic_engine():
    """Lazy load the semantic search engine"""
    global semantic_engine
    if semantic_engine is None:
        print("Loading semantic search engine...")
        semantic_engine = SemanticSearchEngine(model_name='all-MiniLM-L6-v2')
    return semantic_engine

def load_game_embeddings():
    """Load pre-computed game embeddings"""
    global game_embeddings, game_ids
    if game_embeddings is None:
        embeddings_file = 'embeddings/game_embeddings.json'
        if os.path.exists(embeddings_file):
            print("Loading game embeddings from file...")
            game_embeddings, game_ids = load_embeddings(embeddings_file)
            print(f"Loaded {len(game_ids)} game embeddings")
        else:
            print(f"Warning: {embeddings_file} not found. Semantic search won't work.")
    return game_embeddings, game_ids


@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle search requests and query Solr with optional semantic search"""
    try:
        data = request.json
        query_text = data.get('query', '')
        rows = data.get('rows', 10)
        search_mode = data.get('mode', 'keyword')  # 'keyword', 'semantic', or 'hybrid'
        
        if not query_text:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Keyword search mode (default)
        if search_mode == 'keyword':
            return perform_keyword_search(query_text, rows)
        
        # Semantic search mode
        elif search_mode == 'semantic':
            return perform_semantic_search(query_text, rows)
        
        # Hybrid search mode (combines both)
        elif search_mode == 'hybrid':
            return perform_hybrid_search(query_text, rows)
        
        else:
            return jsonify({'error': 'Invalid search mode'}), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def perform_keyword_search(query_text, rows):
    """Perform traditional keyword-based search using Solr"""
    try:
        solr_params = {
            'q': query_text,
            'rows': rows,
            'fl': 'id,title,about_the_game,header_image,release_date,price,developers,genres,categories,tags,score,age_rating_label,release_year_label,price_range_label,OS_label,playtime_label',
            'defType': 'edismax',
            'qf': 'title about_the_game supported_languages developers genres categories tags age_rating_label release_year_label price_range_label OS_label playtime_label',
            'wt': 'json'
        }
        
        uri = f"{SOLR_URI}/{COLLECTION}/select"
        response = requests.post(uri, data=solr_params, timeout=10)
        
        print(f"Keyword search status: {response.status_code}")
        response.raise_for_status()
        
        results = response.json()
        docs = results.get('response', {}).get('docs', [])
        num_found = results.get('response', {}).get('numFound', 0)
        qtime = results.get('responseHeader', {}).get('QTime', 0)
        
        return jsonify({
            'success': True,
            'results': docs,
            'numFound': num_found,
            'qtime': qtime,
            'mode': 'keyword'
        })
        
    except requests.RequestException as e:
        error_msg = f'Solr connection error: {str(e)}'
        if hasattr(e, 'response') and e.response:
            error_msg += f'\nResponse: {e.response.text[:200]}'
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


def perform_semantic_search(query_text, rows):
    """Perform semantic search using embeddings"""
    try:
        # Load semantic search components
        engine = get_semantic_engine()
        embeddings, ids = load_game_embeddings()
        
        if embeddings is None:
            return jsonify({
                'success': False,
                'error': 'Embeddings not available. Run generate_embeddings.py first.'
            }), 500
        
        # Generate query embedding
        query_embedding = engine.encode_text(query_text)
        
        # Find similar games
        similar_games = engine.find_similar(query_embedding, embeddings, top_k=rows)
        
        # Fetch full game details from Solr
        game_ids_to_fetch = [ids[idx] for idx, score in similar_games]
        
        # Build OR query for Solr
        id_query = ' OR '.join([f'id:"{gid}"' for gid in game_ids_to_fetch])
        
        solr_params = {
            'q': id_query,
            'rows': rows,
            'fl': 'id,title,about_the_game,header_image,release_date,price,developers,genres,categories,tags,age_rating_label,release_year_label,price_range_label,OS_label,playtime_label',
            'wt': 'json'
        }
        
        uri = f"{SOLR_URI}/{COLLECTION}/select"
        response = requests.post(uri, data=solr_params, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        docs = results.get('response', {}).get('docs', [])
        
        # Create a map for ordering and adding similarity scores
        id_to_doc = {doc['id']: doc for doc in docs}
        similarity_scores = {ids[idx]: score for idx, score in similar_games}
        
        # Reorder docs according to similarity and add scores
        ordered_docs = []
        for gid in game_ids_to_fetch:
            if gid in id_to_doc:
                doc = id_to_doc[gid]
                doc['semantic_score'] = similarity_scores[gid]
                ordered_docs.append(doc)
        
        return jsonify({
            'success': True,
            'results': ordered_docs,
            'numFound': len(ordered_docs),
            'qtime': results.get('responseHeader', {}).get('QTime', 0),
            'mode': 'semantic'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Semantic search error: {str(e)}'
        }), 500


def perform_hybrid_search(query_text, rows, keyword_weight=0.5):
    """Perform hybrid search combining keyword and semantic approaches"""
    try:
        # Get keyword search results
        keyword_response = perform_keyword_search(query_text, rows * 2)  # Fetch more for reranking
        keyword_data = keyword_response.get_json()
        
        if not keyword_data.get('success'):
            return keyword_response
        
        keyword_docs = keyword_data.get('results', [])
        
        # Get semantic search results
        semantic_response = perform_semantic_search(query_text, rows * 2)
        semantic_data = semantic_response.get_json()
        
        if not semantic_data.get('success'):
            # Fall back to keyword search if semantic fails
            return keyword_response
        
        semantic_docs = semantic_data.get('results', [])
        
        # Combine and rerank results
        engine = get_semantic_engine()
        
        # Create unified document list with hybrid scores
        doc_scores = {}
        
        # Process keyword results (normalize scores)
        max_keyword_score = max([doc.get('score', 0) for doc in keyword_docs]) if keyword_docs else 1.0
        for i, doc in enumerate(keyword_docs):
            doc_id = doc['id']
            # Normalize keyword score (higher position = higher score)
            normalized_score = doc.get('score', 0) / max_keyword_score if max_keyword_score > 0 else 0
            doc_scores[doc_id] = {
                'doc': doc,
                'keyword_score': normalized_score,
                'semantic_score': 0,
                'hybrid_score': 0
            }
        
        # Process semantic results
        for doc in semantic_docs:
            doc_id = doc['id']
            semantic_score = doc.get('semantic_score', 0)
            
            if doc_id in doc_scores:
                doc_scores[doc_id]['semantic_score'] = semantic_score
            else:
                doc_scores[doc_id] = {
                    'doc': doc,
                    'keyword_score': 0,
                    'semantic_score': semantic_score,
                    'hybrid_score': 0
                }
        
        # Calculate hybrid scores
        for doc_id, scores in doc_scores.items():
            scores['hybrid_score'] = engine.hybrid_score(
                scores['keyword_score'],
                scores['semantic_score'],
                keyword_weight
            )
        
        # Sort by hybrid score
        sorted_docs = sorted(doc_scores.values(), key=lambda x: x['hybrid_score'], reverse=True)
        
        # Prepare final results
        final_docs = []
        for item in sorted_docs[:rows]:
            doc = item['doc']
            doc['hybrid_score'] = item['hybrid_score']
            doc['keyword_score'] = item['keyword_score']
            doc['semantic_score'] = item['semantic_score']
            final_docs.append(doc)
        
        return jsonify({
            'success': True,
            'results': final_docs,
            'numFound': len(final_docs),
            'qtime': keyword_data.get('qtime', 0) + semantic_data.get('qtime', 0),
            'mode': 'hybrid'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Hybrid search error: {str(e)}'
        }), 500
    

@app.route('/game/<game_id>')
def game_detail(game_id):
    """Render the detailed game page"""
    return render_template('game_detail.html', game_id=game_id)


@app.route('/api/game/<game_id>', methods=['GET'])
def get_game_detail(game_id):
    """Fetch detailed information for a specific game"""
    try:
        solr_params = {
            'q': f'id:"{game_id}"',
            'rows': 1,
            'fl': '*',  # Fetch all fields
            'wt': 'json'
        }
        
        uri = f"{SOLR_URI}/{COLLECTION}/select"
        response = requests.post(uri, data=solr_params, timeout=10)
        response.raise_for_status()
        
        results = response.json()
        docs = results.get('response', {}).get('docs', [])
        
        if not docs:
            return jsonify({
                'success': False,
                'error': 'Game not found'
            }), 404
        
        return jsonify({
            'success': True,
            'game': docs[0]
        })
        
    except requests.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching game details: {str(e)}'
        }), 500


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Provide autocomplete suggestions"""
    try:
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return jsonify([])
        
        return jsonify([])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
