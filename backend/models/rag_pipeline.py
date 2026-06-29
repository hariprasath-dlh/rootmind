"""
RAG Pipeline for codebase context retrieval.
Connects to Qdrant Cloud and uses local SentenceTransformers for zero-cost embeddings.
"""
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("[WARNING] SentenceTransformers not available - using mock embeddings")
from backend.app.config import get_settings

settings = get_settings()

# Free, fast, local embedding model (produces 384-dimensional vectors)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "rootmind_codebase"

# Global variables to cache models and clients (prevents reloading on every API call)
_embedding_model = None
_qdrant_client = None

def get_embedding_model():
    """Loads the local SentenceTransformer model."""
    global _embedding_model
    if _embedding_model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
        print("? Loading SentenceTransformer model (first time only)...")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model

def get_qdrant_client():
    """Initializes the connection to Qdrant Cloud."""
    global _qdrant_client
    if _qdrant_client is None:
        print("? Connecting to Qdrant Cloud...")
        _qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=False 
        )
    return _qdrant_client

def initialize_collection():
    """Creates the Qdrant collection if it doesn't already exist."""
    client = get_qdrant_client()
    if SENTENCE_TRANSFORMERS_AVAILABLE:
        model = get_embedding_model()
        vector_size = model.get_sentence_embedding_dimension()
    else:
        vector_size = 384
    
    collections = client.get_collections().collections
    collection_exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not collection_exists:
        print(f"? Creating Qdrant collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print("? Collection created.")
    else:
        print(f"? Collection '{COLLECTION_NAME}' already exists.")

def embed_text(text: str) -> list[float]:
    """Converts raw text into a high-dimensional vector embedding."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return [0.0] * 384
    model = get_embedding_model()
    return model.encode(text).tolist()

def upsert_code_chunk(chunk_id: int, file_path: str, code_content: str, commit_hash: str):
    """Inserts or updates a code chunk in the Qdrant collection."""
    client = get_qdrant_client()
    vector = embed_text(code_content)
    
    payload = {
        "file_path": file_path,
        "code_content": code_content,
        "commit_hash": commit_hash
    }
    
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(id=chunk_id, vector=vector, payload=payload)
        ]
    )

def semantic_search(query: str, limit: int = 3) -> list[dict]:
    """Searches the Qdrant collection for code chunks relevant to the query."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("[WARNING] SentenceTransformers not available - returning mock code chunks")
        return [
            {
                "file_path": "src/api/payment_handler.py",
                "code_content": "async def process_payment(amount):\n    # Missing timeout on external API call causes latency spikes\n    response = await external_api.charge(amount)\n    return response",
                "commit_hash": "e4f5g6h",
                "score": 0.9
            }
        ]
    client = get_qdrant_client()
    
    # ?? DEFENSIVE PROGRAMMING: Ensure collection exists before searching
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        print("?? Collection not found during search. Initializing empty collection...")
        initialize_collection()
        return [] # Return empty results if we just created it
        
    query_vector = embed_text(query)
    
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    results = []
    for hit in search_result:
        results.append({
            "file_path": hit.payload["file_path"],
            "code_content": hit.payload["code_content"],
            "commit_hash": hit.payload["commit_hash"],
            "score": hit.score
        })
        
    return results

def seed_mock_codebase():
    """Seeds Qdrant with mock codebase chunks for testing the RAG pipeline."""
    print("? Seeding mock codebase into Qdrant...")
    initialize_collection()
    
    # These mock chunks contain intentional bugs that match our anomaly symptoms
    mock_chunks = [
        {
            "id": 1,
            "file": "src/db/connection_pool.py",
            "content": "def get_db_connection():\n    # Max connections set too low for production load\n    MAX_CONNECTIONS = 10\n    return create_pool(max_size=MAX_CONNECTIONS)",
            "commit": "a1b2c3d"
        },
        {
            "id": 2,
            "file": "src/api/payment_handler.py",
            "content": "async def process_payment(amount):\n    # Missing timeout on external API call causes latency spikes\n    response = await external_api.charge(amount)\n    return response",
            "commit": "e4f5g6h"
        },
        {
            "id": 3,
            "file": "src/utils/cache.py",
            "content": "def cache_user_data(user_id):\n    # Memory leak: appending to global list without clearing\n    global user_cache\n    user_cache.append(fetch_from_db(user_id))",
            "commit": "i7j8k9l"
        },
        {
            "id": 4,
            "file": "src/api/health_check.py",
            "content": "def health():\n    return {'status': 'ok'}",
            "commit": "m0n1o2p"
        }
    ]
    
    for chunk in mock_chunks:
        upsert_code_chunk(chunk["id"], chunk["file"], chunk["content"], chunk["commit"])
        
    print(f"? Seeded {len(mock_chunks)} mock code chunks into Qdrant.")