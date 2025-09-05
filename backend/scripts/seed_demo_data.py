#!/usr/bin/env python3
"""
Seed demo data for IRIS analytics.
- Tips + Assessments across sectors/regions
- PDFCheck samples
- HeatmapBucket aggregates (sector, region)

Idempotent: runs safe upserts by checking existing counts/keys.
"""
from __future__ import annotations
import random
from datetime import datetime, timedelta, date
import os
import sys

# Ensure backend root is on sys.path so `app.*` imports work when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import (
    Tip, Assessment, PDFCheck, HeatmapBucket,
    FraudChain, FraudChainNode, FraudChainEdge
)

SECTORS = [
    "Banking", "Telecom", "IT Services", "Pharma", "NBFC", "Energy", "Real Estate"
]
REGIONS = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata"
]

MESSAGES = [
    "Hot tip: Mid-cap stock expected to rally 20% in 2 weeks",
    "Advisor claims SEBI registration, guaranteed returns",
    "Unusual trading patterns spotted in telecom small-cap",
    "Real estate pre-IPO allocation via WhatsApp group",
]


def ensure_tips_and_assessments(db):
    # Create a few tips if none
    tip_count = db.query(Tip).count()
    if tip_count >= 5:
        return
    for i in range(5):
        t = Tip(message=random.choice(MESSAGES), source="seed")
        db.add(t)
        db.flush()
        level = random.choice(["Low", "Medium", "High"])
        score = {"Low": random.randint(10, 40), "Medium": random.randint(41, 70), "High": random.randint(71, 95)}[level]
        assess = Assessment(
            tip_id=t.id,
            level=level,
            score=score,
            reasons=["pattern_match", "language_red_flags"] if level != "Low" else ["benign_language"],
            stock_symbols=["RELIANCE", "TCS", "BHARTIARTL"][0:random.randint(0, 2)],
            advisor_info={"claimed_sebi_reg": bool(random.getrandbits(1))},
            confidence=random.randint(60, 90),
        )
        db.add(assess)
    db.commit()

def reset_fraud_chains(db):
    """Delete all fraud chain nodes, edges, and chains. Idempotent and safe.

    Note: This does not delete Tips/Assessments/PDFChecks that were referenced by nodes.
    They will remain in their tables. Reseeding will create fresh nodes/edges referencing
    either existing or new records as defined by the seed functions.
    """
    # Import models locally to avoid circulars in type checkers
    from app.models import FraudChainEdge, FraudChainNode, FraudChain

    # Delete in dependency order: edges -> nodes -> chains
    deleted_edges = db.query(FraudChainEdge).delete(synchronize_session=False)
    deleted_nodes = db.query(FraudChainNode).delete(synchronize_session=False)
    deleted_chains = db.query(FraudChain).delete(synchronize_session=False)
    db.commit()
    print(f"Reset fraud chains: edges={deleted_edges}, nodes={deleted_nodes}, chains={deleted_chains}")


def ensure_dense_telegram_chain(db):
    """Ensure the 'Suspicious Telegram Tip Chain' has >=5 tips and >=6 edges.

    Idempotent: Only adds missing nodes/edges.
    """
    chain = db.query(FraudChain).filter(FraudChain.name == "Suspicious Telegram Tip Chain").first()
    if not chain:
        return

    # Fetch existing nodes for this chain
    nodes = db.query(FraudChainNode).filter(FraudChainNode.chain_id == chain.id).all()
    tips = [n for n in nodes if n.node_type == "tip"]
    advisor = next((n for n in nodes if n.node_type == "advisor"), None)
    pdf = next((n for n in nodes if n.node_type == "document"), None)
    assess = next((n for n in nodes if n.node_type == "assessment"), None)

    # Create additional tips up to 5 total
    needed = max(0, 5 - len(tips))
    new_tip_nodes = []
    for i in range(needed):
        t = Tip(message=f"Suspicious Telegram Tip Variant {i+1}", source="telegram")
        db.add(t)
        db.flush()
        tn = FraudChainNode(
            chain_id=chain.id,
            node_type="tip",
            reference_id=t.id,
            label=f"Suspicious Telegram Tip {i+1}",
            position_x=100 + (i+1) * 40,
            position_y=140 + (i%2) * 40,
            node_metadata={"channel": "telegram", "variant": i+1},
        )
        db.add(tn)
        new_tip_nodes.append(tn)
    db.flush()

    # Refresh collections
    if new_tip_nodes:
        tips = tips + new_tip_nodes

    # Ensure edges >= 6 by linking tips to advisor/pdf and cross-linking tips
    edges = db.query(FraudChainEdge).filter(FraudChainEdge.chain_id == chain.id).all()
    def has_edge(a_id, b_id, rel=None):
        for e in edges:
            if e.from_node_id == a_id and e.to_node_id == b_id and (rel is None or e.relationship_type == rel):
                return True
        return False

    # Link each tip to advisor and pdf if present
    for tip_node in tips:
        if advisor and not has_edge(tip_node.id, advisor.id, "mentions"):
            e = FraudChainEdge(
                chain_id=chain.id,
                from_node_id=tip_node.id,
                to_node_id=advisor.id,
                relationship_type="mentions",
                confidence=75,
                edge_metadata={"auto": True},
            )
            db.add(e)
            edges.append(e)
        if pdf and not has_edge(tip_node.id, pdf.id, "references"):
            e = FraudChainEdge(
                chain_id=chain.id,
                from_node_id=tip_node.id,
                to_node_id=pdf.id,
                relationship_type="references",
                confidence=70,
                edge_metadata={"auto": True},
            )
            db.add(e)
            edges.append(e)

    # Add some cross-links between tips to increase edge count
    for i in range(len(tips)):
        for j in range(i+1, len(tips)):
            a, b = tips[i], tips[j]
            if not has_edge(a.id, b.id, "similar_content"):
                e = FraudChainEdge(
                    chain_id=chain.id,
                    from_node_id=a.id,
                    to_node_id=b.id,
                    relationship_type="similar_content",
                    confidence=60,
                    edge_metadata={"ngram_overlap": True},
                )
                db.add(e)
                edges.append(e)
            # Stop excessive growth; 6-10 edges is enough for demo
            if len(edges) >= 10:
                break
        if len(edges) >= 10:
            break
    db.commit()


def ensure_specific_telegram_chain(db):
    """Create the requested fraud chain if it doesn't already exist.

    Scenario:
    - Tip: "Suspicious Telegram Tip" + "High return promise on smallcap"
    - Advisor: "Advisor: Raj Mehta" (SEBI reg pending verification)
    - Document: "PDF: Contract-INV-2024-09.pdf" (Stamp mismatch detected)
    """
    from app.models import FraudChain

    existing = db.query(FraudChain).filter(FraudChain.name == "Suspicious Telegram Tip Chain").first()
    if existing:
        return

    # Create chain
    chain = FraudChain(
        name="Suspicious Telegram Tip Chain",
        description="Telegram tip promising high returns on smallcap with unverified advisor and mismatched contract stamp",
        status="active",
    )
    db.add(chain)
    db.flush()

    # Tip (upsert by message+source)
    tip_msg = "Suspicious Telegram Tip\nHigh return promise on smallcap"
    tip = db.query(Tip).filter(Tip.message == tip_msg, Tip.source == "telegram").first()
    if not tip:
        tip = Tip(message=tip_msg, source="telegram")
        db.add(tip)
        db.flush()

    # Assessment (upsert by tip_id)
    assess = db.query(Assessment).filter(Assessment.tip_id == tip.id).first()
    if not assess:
        assess = Assessment(
            tip_id=tip.id,
            level="High",
            score=90,
            reasons=["high_return_promise", "unsolicited_channel", "pump_signals"],
            stock_symbols=["SMALLCAP"],
            advisor_info={"name": "Raj Mehta", "sebi_registration_status": "pending_verification"},
            confidence=88,
        )
        db.add(assess)
        db.flush()

    # Document (upsert by unique file_hash)
    pdf = db.query(PDFCheck).filter(PDFCheck.file_hash == "contract-inv-2024-09").first()
    if not pdf:
        pdf = PDFCheck(
            file_hash="contract-inv-2024-09",
            filename="Contract-INV-2024-09.pdf",
            file_size=180000,
            ocr_text="Investment contract showing inconsistent stamp and unverifiable terms",
            anomalies=["Stamp mismatch detected"],
            score=58,
            is_likely_fake=True,
            processing_time_ms=1200,
        )
        db.add(pdf)
        db.flush()

    # Nodes
    n_tip = FraudChainNode(
        chain_id=chain.id,
        node_type="tip",
        reference_id=tip.id,
        label="Suspicious Telegram Tip",
        position_x=100,
        position_y=100,
        node_metadata={"channel": "telegram"},
    )
    n_assess = FraudChainNode(
        chain_id=chain.id,
        node_type="assessment",
        reference_id=assess.id,
        label="Risk: High (90%)",
        position_x=300,
        position_y=100,
        node_metadata={"level": "High", "score": 90, "stock_symbols": ["SMALLCAP"]},
    )
    n_adv = FraudChainNode(
        chain_id=chain.id,
        node_type="advisor",
        reference_id="raj-mehta",
        label="Advisor: Raj Mehta",
        position_x=100,
        position_y=260,
        node_metadata={"sebi_status": "pending_verification"},
    )
    n_pdf = FraudChainNode(
        chain_id=chain.id,
        node_type="document",
        reference_id=pdf.id,
        label="PDF: Contract-INV-2024-09.pdf",
        position_x=300,
        position_y=260,
        node_metadata={"anomalies": ["Stamp mismatch detected"]},
    )
    db.add_all([n_tip, n_assess, n_adv, n_pdf])
    db.flush()

    # Edges
    e_tip_to_assess = FraudChainEdge(
        chain_id=chain.id,
        from_node_id=n_tip.id,
        to_node_id=n_assess.id,
        relationship_type="leads_to",
        confidence=98,
        edge_metadata={"source": "analysis"},
    )
    e_tip_mentions_adv = FraudChainEdge(
        chain_id=chain.id,
        from_node_id=n_tip.id,
        to_node_id=n_adv.id,
        relationship_type="mentions",
        confidence=85,
        edge_metadata={"mention": "advisor_mentioned_in_tip"},
    )
    e_tip_references_pdf = FraudChainEdge(
        chain_id=chain.id,
        from_node_id=n_tip.id,
        to_node_id=n_pdf.id,
        relationship_type="references",
        confidence=80,
        edge_metadata={"reference": "contract_attached"},
    )
    db.add_all([e_tip_to_assess, e_tip_mentions_adv, e_tip_references_pdf])
    db.commit()

def ensure_pdf_checks(db):
    pdf_count = db.query(PDFCheck).count()
    if pdf_count >= 2:
        return
    anomalies_list = [
        ["Missing watermark"],
        ["Font mismatch", "Inconsistent formatting"],
        [],
    ]
    for i in range(2):
        chk = PDFCheck(
            file_hash=f"seed_hash_{i}",
            filename=f"sample_{i}.pdf",
            file_size=100000 + i * 500,
            ocr_text="Sample extracted text",
            anomalies=random.choice(anomalies_list),
            score=random.randint(60, 95),
            is_likely_fake=bool(random.getrandbits(1)),
            processing_time_ms=random.randint(500, 3000),
        )
        db.add(chk)
    db.commit()


def upsert_heatmap_bucket(db, dimension: str, key: str, total: int, high: int, medium: int, low: int):
    today = date.today()
    from_d = today - timedelta(days=30)
    bucket = (
        db.query(HeatmapBucket)
        .filter(
            HeatmapBucket.dimension == dimension,
            HeatmapBucket.key == key,
            HeatmapBucket.from_date == from_d,
            HeatmapBucket.to_date == today,
        )
        .first()
    )
    if not bucket:
        bucket = HeatmapBucket(
            dimension=dimension,
            key=key,
            from_date=from_d,
            to_date=today,
            total_count=total,
            high_risk_count=high,
            medium_risk_count=medium,
            low_risk_count=low,
        )
        db.add(bucket)
    else:
        bucket.total_count = total
        bucket.high_risk_count = high
        bucket.medium_risk_count = medium
        bucket.low_risk_count = low
        bucket.last_updated = datetime.utcnow()


def ensure_heatmap_buckets(db):
    # Only seed if there are few buckets
    existing = db.query(HeatmapBucket).count()
    if existing >= 10:
        return
    # Sectors
    for s in SECTORS:
        total = random.randint(5, 40)
        high = random.randint(0, total // 2)
        medium = random.randint(0, (total - high) // 2)
        low = max(0, total - high - medium)
        upsert_heatmap_bucket(db, "sector", s, total, high, medium, low)
    # Regions
    for r in REGIONS:
        total = random.randint(3, 30)
        high = random.randint(0, total // 2)
        medium = random.randint(0, (total - high) // 2)
        low = max(0, total - high - medium)
        upsert_heatmap_bucket(db, "region", r, total, high, medium, low)
    db.commit()


def ensure_fraud_chain(db):
    """Create a demo fraud chain with linked nodes and edges if none exists."""
    existing = db.query(FraudChain).count()
    if existing > 0:
        return
    chain = FraudChain(name="Demo Fraud Case", description="Seeded demo chain with linked entities")
    db.add(chain)
    db.flush()

    # Create a tip and pdf to reference
    tip = Tip(message="Seed chain tip: suspicious advisor and stock claims", source="seed")
    db.add(tip)
    db.flush()
    assess = Assessment(
        tip_id=tip.id,
        level="High",
        score=88,
        reasons=["advisor_claims", "pump_language"],
        stock_symbols=["RELIANCE"],
        advisor_info={"claimed_sebi_reg": False},
        confidence=85,
    )
    db.add(assess)
    db.flush()

    pdf = PDFCheck(
        file_hash="seed_chain_pdf_hash",
        filename="chain_doc.pdf",
        file_size=120000,
        ocr_text="This is a seeded document used for demo chain",
        anomalies=["Missing watermark"],
        score=62,
        is_likely_fake=True,
        processing_time_ms=1500,
    )
    db.add(pdf)
    db.flush()

    # Nodes
    n_tip = FraudChainNode(chain_id=chain.id, node_type="tip", reference_id=tip.id, label="Suspicious Tip")
    n_pdf = FraudChainNode(chain_id=chain.id, node_type="document", reference_id=pdf.id, label="Questionable PDF")
    n_adv = FraudChainNode(chain_id=chain.id, node_type="advisor", reference_id="seed-advisor-1", label="Unregistered Advisor")
    db.add_all([n_tip, n_pdf, n_adv])
    db.flush()

    # Edges (links)
    e1 = FraudChainEdge(chain_id=chain.id, from_node_id=n_tip.id, to_node_id=n_adv.id, relationship_type="mentions", confidence=90)
    e2 = FraudChainEdge(chain_id=chain.id, from_node_id=n_tip.id, to_node_id=n_pdf.id, relationship_type="references", confidence=80)
    db.add_all([e1, e2])
    db.commit()


def main():
    # Simple CLI handling
    args = sys.argv[1:]
    db = SessionLocal()
    try:
        if "--reset-chains" in args:
            reset_fraud_chains(db)
            # Recreate only the specific Telegram chain (plus densify it)
            ensure_specific_telegram_chain(db)
            ensure_dense_telegram_chain(db)
            print("Reset and recreated Telegram fraud chain successfully.")
        else:
            ensure_tips_and_assessments(db)
            ensure_pdf_checks(db)
            ensure_heatmap_buckets(db)
            ensure_fraud_chain(db)
            ensure_specific_telegram_chain(db)
            ensure_dense_telegram_chain(db)
            print("Seeded demo data successfully.")
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
