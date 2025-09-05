import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

from elasticsearch import Elasticsearch, helpers  # type: ignore

# Ensure app imports work when running as a script
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.database import SessionLocal  # type: ignore
from app.models import Tip, Assessment, PDFCheck  # type: ignore

MAPPINGS_PATH = ROOT / "schema" / "es_mappings.json"

RISK_RANK = {"Low": 1, "Medium": 2, "High": 3}


def load_mappings() -> Dict[str, Any]:
    with open(MAPPINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_index(client: Elasticsearch, index_name: str, mappings: Dict[str, Any]):
    if not client.indices.exists(index=index_name):
        client.indices.create(index=index_name, body=mappings)


def risk_from_assessment(ass: Optional[Assessment]) -> Dict[str, Any]:
    if not ass:
        return {"risk": None, "risk_rank": None, "risk_score": None}
    return {
        "risk": ass.level,
        "risk_rank": RISK_RANK.get(ass.level),
        "risk_score": float(ass.score) if ass.score is not None else None,
    }


def index_tips(session, client: Elasticsearch, index_name: str):
    # For each tip, attach latest assessment if exists
    tips = session.query(Tip).all()
    for tip in tips:
        # latest assessment by created_at
        latest_ass = None
        if tip.assessments:
            latest_ass = sorted(tip.assessments, key=lambda a: a.created_at or datetime.min)[-1]
        risk_info = risk_from_assessment(latest_ass)
        doc = {
            "id": tip.id,
            "entity_type": "tip",
            "title": None,
            "message": tip.message,
            "summary": None,
            "content": None,
            "name": None,
            "company": None,
            "symbols_text": ",".join(latest_ass.stock_symbols) if latest_ass and latest_ass.stock_symbols else None,
            "risk": risk_info["risk"],
            "risk_rank": risk_info["risk_rank"],
            "risk_score": risk_info["risk_score"],
            "sector": None,
            "region": None,
            "created_at": (tip.created_at.isoformat() if isinstance(tip.created_at, datetime) else None),
            "extra": {
                "source": tip.source,
                "submitter_id": tip.submitter_id,
            },
        }
        client.index(index=index_name, id=tip.id, body=doc, refresh=False)


def index_assessments(session, client: Elasticsearch, index_name: str):
    assessments = session.query(Assessment).all()
    for ass in assessments:
        risk_info = risk_from_assessment(ass)
        doc = {
            "id": ass.id,
            "entity_type": "assessment",
            "title": f"Assessment {ass.level} ({ass.score})",
            "message": None,
            "summary": "; ".join(ass.reasons) if ass.reasons else None,
            "content": None,
            "name": None,
            "company": None,
            "symbols_text": ",".join(ass.stock_symbols) if ass.stock_symbols else None,
            "risk": risk_info["risk"],
            "risk_rank": risk_info["risk_rank"],
            "risk_score": risk_info["risk_score"],
            "sector": None,
            "region": None,
            "created_at": (ass.created_at.isoformat() if isinstance(ass.created_at, datetime) else None),
            "extra": {
                "tip_id": ass.tip_id,
                "advisor_info": ass.advisor_info,
                "confidence": ass.confidence,
            },
        }
        client.index(index=index_name, id=ass.id, body=doc, refresh=False)


def index_documents(session, client: Elasticsearch, index_name: str):
    pdfs = session.query(PDFCheck).all()
    for docu in pdfs:
        # Map document risk
        risk_level = None
        risk_score = None
        if docu.is_likely_fake is not None:
            risk_level = "High" if docu.is_likely_fake else "Low"
        if docu.score is not None:
            risk_score = float(docu.score)
        doc = {
            "id": docu.id,
            "entity_type": "document",
            "title": docu.filename,
            "message": None,
            "summary": None,
            "content": docu.ocr_text,
            "name": None,
            "company": None,
            "symbols_text": None,
            "risk": risk_level,
            "risk_rank": RISK_RANK.get(risk_level) if risk_level else None,
            "risk_score": risk_score,
            "sector": None,
            "region": None,
            "created_at": (docu.created_at.isoformat() if isinstance(docu.created_at, datetime) else None),
            "extra": {
                "file_size": docu.file_size,
                "anomalies": docu.anomalies,
                "processing_time_ms": docu.processing_time_ms,
            },
        }
        client.index(index=index_name, id=docu.id, body=doc, refresh=False)


def main():
    es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    indices_env = os.getenv("ELASTICSEARCH_INDICES", "tips,advisors,documents,assessments")
    indices = [i.strip() for i in indices_env.split(",") if i.strip()]

    client = Elasticsearch(es_url)
    mappings = load_mappings()

    # Ensure indices exist (use same mapping per index for simplicity)
    for idx in indices:
        # Only create for known indices we index here
        if idx in ("tips", "documents", "assessments"):
            ensure_index(client, idx, mappings)

    session = SessionLocal()
    try:
        if "tips" in indices:
            index_tips(session, client, "tips")
        if "assessments" in indices:
            index_assessments(session, client, "assessments")
        if "documents" in indices:
            index_documents(session, client, "documents")

        # Refresh indices for immediate searchability
        for idx in ("tips", "documents", "assessments"):
            if client.indices.exists(index=idx):
                client.indices.refresh(index=idx)
        print("Indexing completed.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
