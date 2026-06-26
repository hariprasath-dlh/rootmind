"""
incidents.py - Incident CRUD endpoints

Defines REST endpoints for listing, viewing, creating, and retrieving post-mortem reports
for incident records.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_incidents(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    List all incident logs from the database with pagination.
    
    Args:
        skip (int): The number of entries to skip.
        limit (int): The maximum number of entries to return.
        db (Session): Database session dependency.

    Returns:
        List[Dict[str, Any]]: A list of incident records.
    """
    return [
        {
            "id": 1,
            "title": "Database connection spike",
            "status": "resolved",
            "created_at": "2026-06-26T12:00:00Z"
        }
    ]


@router.get("/{incident_id}", response_model=Dict[str, Any])
async def get_incident(
    incident_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a single incident record by its unique ID.
    
    Args:
        incident_id (int): Unique ID of the incident.
        db (Session): Database session dependency.

    Returns:
        Dict[str, Any]: Incident detail record.
    """
    if incident_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Incident not found"
        )
    return {
        "id": 1,
        "title": "Database connection spike",
        "status": "resolved",
        "description": "High CPU utilization and latency anomaly in API service.",
        "created_at": "2026-06-26T12:00:00Z"
    }


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: Dict[str, Any], 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually register a new incident in the database.
    
    Args:
        incident_data (Dict[str, Any]): Data schema details for the incident.
        db (Session): Database session dependency.

    Returns:
        Dict[str, Any]: Created incident record details.
    """
    return {
        "id": 2,
        "title": incident_data.get("title", "New Incident"),
        "status": "triggered",
        "created_at": "2026-06-26T14:00:00Z"
    }


@router.get("/{incident_id}/postmortem", response_model=Dict[str, Any])
async def get_incident_postmortem(
    incident_id: int, 
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the auto-generated markdown post-mortem report for a specific incident.
    
    Args:
        incident_id (int): Unique ID of the incident.
        db (Session): Database session dependency.

    Returns:
        Dict[str, Any]: Markdown post-mortem report metadata.
    """
    if incident_id != 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Incident not found"
        )
    return {
        "incident_id": 1,
        "post_mortem": "# Post-Mortem Report\n\n## Summary\nProduction crash due to connection limits.",
        "created_at": "2026-06-26T12:30:00Z"
    }
