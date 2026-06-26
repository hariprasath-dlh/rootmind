"""
Memory Engine for long-term incident pattern recognition.
Stores resolved incidents in Qdrant for future reference.
"""
from typing import Optional
from qdrant_client.models import PointStruct
from backend.models.rag_pipeline import get_qdrant_client, embed_text, initialize_collection
from backend.app.config import get_settings

settings = get_settings()
MEMORY_COLLECTION_NAME = "rootmind_incident_memory"


def initialize_memory_collection():
    """Creates the incident memory collection if it doesn't exist."""
    client = get_qdrant_client()
    collections = client.get_collections().collections
    collection_exists = any(c.name == MEMORY_COLLECTION_NAME for c in collections)
    
    if not collection_exists:
        print(f"📦 Creating memory collection '{MEMORY_COLLECTION_NAME}'...")
        from qdrant_client.models import Distance, VectorParams
        client.create_collection(
            collection_name=MEMORY_COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print("✅ Memory collection created.")


def store_incident(incident_data: dict, incident_id: str):
    """
    Stores a resolved incident in the memory collection for future pattern recognition.
    """
    print(f"🧠 Memory Engine: Storing incident {incident_id}...")
    
    initialize_memory_collection()
    client = get_qdrant_client()
    
    # Create a searchable text representation of the incident
    searchable_text = f"""
    Service: {incident_data.get('service', 'unknown')}
    Root Cause: {incident_data.get('rca_report', {}).get('root_cause', {}).get('root_cause_summary', '')}
    Technical Explanation: {incident_data.get('rca_report', {}).get('root_cause', {}).get('technical_explanation', '')}
    Responsible File: {incident_data.get('rca_report', {}).get('root_cause', {}).get('responsible_file', '')}
    Fix: {incident_data.get('fix_suggestion', {}).get('fix', {}).get('explanation', '')}
    """
    
    # Generate embedding
    vector = embed_text(searchable_text)
    
    # Store in Qdrant
    payload = {
        "incident_id": incident_id,
        "service": incident_data.get("service", "unknown"),
        "timestamp": incident_data.get("timestamp", ""),
        "root_cause": incident_data.get("rca_report", {}).get("root_cause", {}).get("root_cause_summary", ""),
        "responsible_file": incident_data.get("rca_report", {}).get("root_cause", {}).get("responsible_file", ""),
        "fix_summary": incident_data.get("fix_suggestion", {}).get("fix", {}).get("explanation", ""),
        "searchable_text": searchable_text
    }
    
    # Use incident_id as the point ID (convert string to int hash)
    point_id = hash(incident_id) % 1000000
    
    client.upsert(
        collection_name=MEMORY_COLLECTION_NAME,
        points=[
            PointStruct(id=point_id, vector=vector, payload=payload)
        ]
    )
    
    print(f"✅ Incident {incident_id} stored in memory.")


def find_similar_incidents(current_incident: dict, limit: int = 3) -> list[dict]:
    """
    Searches for similar past incidents to provide context for RCA.
    """
    print("🔍 Memory Engine: Searching for similar past incidents...")
    
    initialize_memory_collection()
    client = get_qdrant_client()
    
    # Create query text from current incident
    query_text = f"""
    Service: {current_incident.get('service', 'unknown')}
    Symptoms: High CPU, High Memory, Extreme Latency, High Error Rate
    """
    
    query_vector = embed_text(query_text)
    
    # Search for similar incidents
    search_result = client.search(
        collection_name=MEMORY_COLLECTION_NAME,
        query_vector=query_vector,
        limit=limit
    )
    
    similar_incidents = []
    for hit in search_result:
        similar_incidents.append({
            "incident_id": hit.payload.get("incident_id", "unknown"),
            "service": hit.payload.get("service", "unknown"),
            "root_cause": hit.payload.get("root_cause", ""),
            "responsible_file": hit.payload.get("responsible_file", ""),
            "similarity_score": hit.score
        })
    
    print(f"✅ Found {len(similar_incidents)} similar past incidents.")
    return similar_incidents