"""
Root Cause Analysis (RCA) Agent.
Uses RAG to find relevant code and LLM to diagnose the incident.
"""
import json
from backend.models.rag_pipeline import semantic_search
from backend.services.groq_service import query_llm

def analyze_root_cause(anomaly_report: dict, repo_url: str = None) -> dict:
    """
    Main entry point for the RCA Agent.
    """
    print("[SEARCH] RCA Agent: Starting Root Cause Analysis...")
    
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
    
    # 2. Retrieve relevant code context (from GitHub or Qdrant)
    context_str = ""
    source_type = "Qdrant Vector DB"
    
    if repo_url:
        print(f"[SEARCH] RCA Agent: Fetching real commit history from GitHub repository: {repo_url}...")
        try:
            from backend.services.github_service import GitHubService
            gh = GitHubService()
            commits = gh.fetch_recent_commits(repo_url, limit=5)
            if commits:
                source_type = "GitHub Repository"
                context_str += "\n--- Recent GitHub Commit History & Code Changes ---\n"
                for i, commit in enumerate(commits):
                    context_str += f"\nCommit {i+1}:\n"
                    context_str += f"SHA: {commit['sha']}\n"
                    context_str += f"Author: {commit['author']}\n"
                    context_str += f"Message: {commit['message']}\n"
                    context_str += f"Date: {commit['date']}\n"
                    
                    # Fetch diff for the commit to understand changes
                    diff = gh.fetch_commit_diff(repo_url, commit['sha'])
                    if diff:
                        # Truncate diff to avoid prompt token overflow
                        context_str += f"Diff Snippet:\n{diff[:1200]}\n"
                    context_str += "-----------------------------------------------\n"
            else:
                print("[WARN] GitHub fetch returned no commits. Falling back to Qdrant...")
        except Exception as e:
            print(f"[ERROR] GitHub integration failed, falling back to Qdrant: {e}")
            
    if not context_str:
        print("[SEARCH] RCA Agent: Searching codebase via RAG...")
        relevant_chunks = semantic_search(query_text, limit=3)
        if not relevant_chunks:
            return {
                "agent": "rca_agent",
                "status": "failed",
                "reason": "No relevant code chunks found in codebase."
            }
        for i, chunk in enumerate(relevant_chunks):
            context_str += f"\n--- Snippet {i+1} (File: {chunk['file_path']}, Commit: {chunk['commit_hash']}) ---\n{chunk['code_content']}\n"

    # 4. Prompt the LLM to find the root cause
    prompt = f"""
    You are an expert Site Reliability Engineer (SRE) and RootMind AI assistant.
    A production incident has occurred with the following symptoms:
    {query_text}
    
    I have retrieved the following codebase context from {source_type}:
    {context_str}
    
    Based on the symptoms and the codebase context, identify the exact root cause of the incident.
    You MUST output your response in the following strict JSON format:
    {{
        "root_cause_summary": "A brief 1-2 sentence explanation of what broke.",
        "responsible_file": "The exact file path (from context or suspected file) that caused the issue.",
        "suspected_commit": "The suspected commit hash.",
        "technical_explanation": "A detailed explanation of why this code/commit caused the specific symptoms.",
        "confidence_score": 0.95
    }}
    Do not include any text outside the JSON block. Do not include markdown formatting like ```json.
    """
    
    print("[AI] RCA Agent: Querying Groq LLM for root cause...")
    llm_response = query_llm(prompt)
    
    # 5. Parse the JSON response safely
    try:
        clean_response = llm_response.replace("```json", "").replace("```", "").strip()
        parsed_response = json.loads(clean_response)
        
        rca_result = {
            "agent": "rca_agent",
            "status": "completed",
            "root_cause": parsed_response
        }
        print(f"[OK] RCA Agent: Root cause identified in {parsed_response.get('responsible_file')}")
        return rca_result
        
    except json.JSONDecodeError:
        print("[WARN] RCA Agent: Failed to parse LLM JSON response. Returning raw text.")
        return {
            "agent": "rca_agent",
            "status": "completed",
            "root_cause": {
                "root_cause_summary": "Failed to parse LLM JSON response.",
                "responsible_file": "unknown",
                "suspected_commit": "unknown",
                "technical_explanation": llm_response,
                "confidence_score": 0.5
            }
        }