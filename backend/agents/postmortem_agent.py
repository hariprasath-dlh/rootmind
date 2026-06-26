"""
Post-Mortem Writer Agent.
Auto-generates comprehensive incident reports in Markdown format.
"""
import json
from datetime import datetime
from backend.services.groq_service import query_llm


def generate_postmortem(incident_data: dict) -> dict:
    """
    Main entry point for the Post-Mortem Writer Agent.
    Generates a professional incident report.
    """
    print("📄 Post-Mortem Writer: Starting report generation...")
    
    # Extract data from the incident
    service = incident_data.get("service", "unknown")
    timestamp = incident_data.get("timestamp", datetime.now().isoformat())
    anomaly = incident_data.get("anomaly_report", {})
    rca = incident_data.get("rca_report", {})
    fix = incident_data.get("fix_suggestion", {})
    
    # Format the data for the LLM
    incident_summary = f"""
    SERVICE: {service}
    INCIDENT TIME: {timestamp}
    
    ANOMALY DETAILS:
    - CPU Usage: {anomaly.get('assessment', {}).get('features', {}).get('cpu_usage', 'N/A')}%
    - Memory Usage: {anomaly.get('assessment', {}).get('features', {}).get('memory_usage', 'N/A')}%
    - Request Latency: {anomaly.get('assessment', {}).get('features', {}).get('request_latency_ms', 'N/A')}ms
    - Error Rate: {anomaly.get('assessment', {}).get('features', {}).get('error_rate', 'N/A')}%
    
    ROOT CAUSE:
    {rca.get('root_cause', {}).get('root_cause_summary', 'N/A')}
    
    TECHNICAL EXPLANATION:
    {rca.get('root_cause', {}).get('technical_explanation', 'N/A')}
    
    RESPONSIBLE FILE: {rca.get('root_cause', {}).get('responsible_file', 'N/A')}
    SUSPECTED COMMIT: {rca.get('root_cause', {}).get('suspected_commit', 'N/A')}
    
    SUGGESTED FIX:
    {fix.get('fix', {}).get('explanation', 'N/A')}
    
    RISK LEVEL: {fix.get('fix', {}).get('risk_level', 'N/A')}
    """
    
    # Prompt the LLM to generate a post-mortem report
    prompt = f"""
    You are an expert Site Reliability Engineer at RootMind AI.
    Generate a professional incident post-mortem report in Markdown format.
    
    INCIDENT DATA:
    {incident_summary}
    
    Your post-mortem MUST include these sections:
    
    # Incident Post-Mortem Report
    
    ## Executive Summary
    (2-3 sentence overview of the incident)
    
    ## Incident Timeline
    (Bullet points with timestamps showing the sequence of events)
    
    ## Root Cause Analysis
    (Detailed technical explanation of what went wrong)
    
    ## Impact Assessment
    (What was affected, estimated downtime, business impact)
    
    ## Resolution
    (How the issue was fixed, including the code patch)
    
    ## Preventive Measures
    (Action items to prevent similar incidents in the future)
    
    ## Lessons Learned
    (Key takeaways for the engineering team)
    
    Format the report professionally with proper Markdown syntax.
    Do not include any text outside the Markdown report.
    """
    
    print("🧠 Post-Mortem Writer: Querying Groq LLM for report...")
    llm_response = query_llm(prompt)
    
    # Generate a unique incident ID
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    postmortem_result = {
        "agent": "postmortem_writer",
        "status": "completed",
        "incident_id": incident_id,
        "report": llm_response,
        "generated_at": datetime.now().isoformat()
    }
    
    print(f"✅ Post-Mortem Writer: Generated report {incident_id}")
    return postmortem_result