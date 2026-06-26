"""
Fix Suggester Agent.
Generates specific code patches to resolve the identified root cause.
"""
import json
from backend.models.rag_pipeline import semantic_search
from backend.services.groq_service import query_llm


def generate_fix(rca_report: dict) -> dict:
    """
    Main entry point for the Fix Suggester Agent.
    Takes the RCA report and generates a specific code patch.
    """
    print("🛠️  Fix Suggester: Starting fix generation...")
    
    # Extract root cause details
    root_cause = rca_report.get("root_cause", {})
    responsible_file = root_cause.get("responsible_file", "unknown")
    technical_explanation = root_cause.get("technical_explanation", "")
    root_cause_summary = root_cause.get("root_cause_summary", "")
    
    # Search for the problematic code to include in context
    query = f"Code from {responsible_file} that causes {root_cause_summary}"
    relevant_chunks = semantic_search(query, limit=2)
    
    # Format the problematic code
    code_context = ""
    for chunk in relevant_chunks:
        if chunk["file_path"] == responsible_file:
            code_context = chunk["code_content"]
            break
    
    if not code_context and relevant_chunks:
        code_context = relevant_chunks[0]["code_content"]
    
    # Prompt the LLM to generate a fix
    prompt = f"""
    You are an expert Site Reliability Engineer at RootMind AI.
    
    A production incident has been diagnosed with the following details:
    
    ROOT CAUSE SUMMARY: {root_cause_summary}
    
    TECHNICAL EXPLANATION: {technical_explanation}
    
    PROBLEMATIC CODE (from {responsible_file}):
    ```
    {code_context}
    ```
    
    Your task is to generate a specific, actionable code fix that resolves this issue.
    
    You MUST output your response in the following strict JSON format:
    {{
        "patch_diff": "A unified diff format showing the exact changes to make (old code with - prefix, new code with + prefix)",
        "fixed_code": "The complete corrected code block",
        "explanation": "A clear explanation of why this fix resolves the issue",
        "risk_level": "LOW, MEDIUM, or HIGH",
        "testing_suggestions": ["List", "of", "test", "cases", "to", "verify", "the", "fix"]
    }}
    
    Do not include any text outside the JSON block. Do not include markdown formatting like ```json.
    """
    
    print("🧠 Fix Suggester: Querying Groq LLM for code patch...")
    llm_response = query_llm(prompt)
    
    # Parse the JSON response
    try:
        clean_response = llm_response.replace("```json", "").replace("```", "").strip()
        parsed_response = json.loads(clean_response)
        
        fix_result = {
            "agent": "fix_suggester",
            "status": "completed",
            "fix": parsed_response,
            "target_file": responsible_file
        }
        print(f"✅ Fix Suggester: Generated patch for {responsible_file}")
        return fix_result
        
    except json.JSONDecodeError:
        print("⚠️ Fix Suggester: Failed to parse LLM JSON response. Returning raw text.")
        return {
            "agent": "fix_suggester",
            "status": "completed",
            "fix": llm_response,
            "target_file": responsible_file
        }