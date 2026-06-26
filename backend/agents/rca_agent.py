"""
Root Cause Analysis (RCA) Agent.
Uses RAG to find relevant code and LLM to diagnose the incident.
"""
import json
from backend.models.rag_pipeline import semantic_search
from backend.services.groq_service import query_llm

def analyze_root_cause(anomaly_report: dict) -> dict:
    """
    Main entry point for the RCA Agent.
    """
    print("🔍 RCA Agent: Starting Root Cause Analysis...")
    
    # 1. Extract context from the anomaly report
    service = anomaly_report.get("service", "unknown")
    assessment = anomaly_report.get("assessment", {})
    features = assessment.get("features", {})
    
    # Create a descriptive query for the RAG pipeline
    query_text = f"""
    Production incident detected for service: {service}.
    Symptoms: High CPU ({features.get('cpu_usage')}%), 
    High Memory ({features.get('memory_usage')}%), 
    Extreme Latency ({features.get('request_latency_ms')}ms), 
    High Error Rate ({features.get('error_rate')}%).
    What code could cause these specific symptoms?
    """
    
    # 2. Retrieve relevant code chunks from Qdrant
    print("🔎 RCA Agent: Searching codebase via RAG...")
    relevant_chunks = semantic_search(query_text, limit=3)
    
    if not relevant_chunks:
        return {
            "agent": "rca_agent",
            "status": "failed",
            "reason": "No relevant code chunks found in vector database."
        }
        
    # 3. Format context for the LLM
    context_str = ""
    for i, chunk in enumerate(relevant_chunks):
        context_str += f"\n--- Snippet {i+1} (File: {chunk['file_path']}, Commit: {chunk['commit_hash']}) ---\n{chunk['code_content']}\n"
        
    # 4. Prompt the LLM to find the root cause
    prompt = f"""
    You are an expert Site Reliability Engineer (SRE) and RootMind AI assistant.
    A production incident has occurred with the following symptoms:
    {query_text}
    
    I have retrieved the following potentially relevant code snippets from the repository:
    {context_str}
    
    Based on the symptoms and the code snippets, identify the exact root cause of the incident.
    You MUST output your response in the following strict JSON format:
    {{
        "root_cause_summary": "A brief 1-2 sentence explanation of what broke.",
        "responsible_file": "The exact file path from the snippets that caused the issue.",
        "suspected_commit": "The commit hash from the snippet.",
        "technical_explanation": "A detailed explanation of why this code caused the specific symptoms.",
        "confidence_score": 0.95
    }}
    Do not include any text outside the JSON block. Do not include markdown formatting like ```json.
    """
    
    print("🧠 RCA Agent: Querying Groq LLM for root cause...")
    llm_response = query_llm(prompt)
    
    # 5. Parse the JSON response safely
    try:
        # Clean up any accidental markdown formatting from the LLM
        clean_response = llm_response.replace("```json", "").replace("```", "").strip()
        parsed_response = json.loads(clean_response)
        
        rca_result = {
            "agent": "rca_agent",
            "status": "completed",
            "root_cause": parsed_response
        }
        print(f"✅ RCA Agent: Root cause identified in {parsed_response.get('responsible_file')}")
        return rca_result
        
    except json.JSONDecodeError:
        print("⚠️ RCA Agent: Failed to parse LLM JSON response. Returning raw text.")
        return {
            "agent": "rca_agent",
            "status": "completed",
            "root_cause": llm_response
        }