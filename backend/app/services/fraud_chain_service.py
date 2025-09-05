from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models import FraudChain, FraudChainNode, FraudChainEdge, Tip, Assessment, PDFCheck
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import csv
import io
from fastapi.responses import StreamingResponse
import re

class FraudChainService:
    def __init__(self, db: Session):
        self.db = db

    async def get_fraud_chains(self, status: Optional[str] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of fraud chains with basic information"""
        query = self.db.query(FraudChain)
        
        if status:
            query = query.filter(FraudChain.status == status)
        
        chains = query.offset(offset).limit(limit).all()
        
        result = []
        for chain in chains:
            try:
                node_count = (
                    self.db.query(func.count(FraudChainNode.id))
                    .filter(FraudChainNode.chain_id == chain.id)
                    .scalar()
                )
                edge_count = (
                    self.db.query(func.count(FraudChainEdge.id))
                    .filter(FraudChainEdge.chain_id == chain.id)
                    .scalar()
                )

                result.append({
                    "id": chain.id,
                    "name": chain.name,
                    "description": chain.description,
                    "status": chain.status or "unknown",
                    "node_count": node_count,
                    "edge_count": edge_count,
                    "created_at": chain.created_at,
                    "updated_at": chain.updated_at,
                })
            except Exception as e:
                # Skip malformed chain rows but continue serving the list
                print(f"Warning: failed to serialize fraud chain {getattr(chain, 'id', 'unknown')}: {e}")
                continue
        
        return result

    async def get_fraud_chain_by_id(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed fraud chain with nodes and edges"""
        chain = self.db.query(FraudChain).filter(FraudChain.id == chain_id).first()
        
        if not chain:
            return None
        
        # Get nodes with enriched data
        nodes = []
        for node in chain.nodes:
            node_data = {
                "id": node.id,
                "node_type": node.node_type,
                "reference_id": node.reference_id,
                "label": node.label,
                "metadata": node.node_metadata,
                "position_x": node.position_x,
                "position_y": node.position_y,
                "created_at": node.created_at
            }
            
            # Enrich with reference data
            reference_data = await self._get_reference_data(node.node_type, node.reference_id)
            if reference_data:
                node_data["metadata"]["reference_data"] = reference_data
            
            nodes.append(node_data)
        
        # Get edges
        edges = []
        for edge in chain.edges:
            edges.append({
                "id": edge.id,
                "from_node_id": edge.from_node_id,
                "to_node_id": edge.to_node_id,
                "relationship_type": edge.relationship_type,
                "confidence": edge.confidence,
                "metadata": edge.edge_metadata,
                "created_at": edge.created_at
            })
        
        return {
            "id": chain.id,
            "name": chain.name,
            "description": chain.description,
            "status": chain.status,
            "created_at": chain.created_at,
            "updated_at": chain.updated_at,
            "nodes": nodes,
            "edges": edges
        }

    async def _get_reference_data(self, node_type: str, reference_id: str) -> Optional[Dict[str, Any]]:
        """Get reference data for a node based on its type"""
        try:
            if node_type == "tip":
                tip = self.db.query(Tip).filter(Tip.id == reference_id).first()
                if tip:
                    return {
                        "message": tip.message[:100] + "..." if len(tip.message) > 100 else tip.message,
                        "source": tip.source,
                        "created_at": tip.created_at.isoformat()
                    }
            
            elif node_type == "assessment":
                assessment = self.db.query(Assessment).filter(Assessment.id == reference_id).first()
                if assessment:
                    return {
                        "level": assessment.level,
                        "score": assessment.score,
                        "stock_symbols": assessment.stock_symbols,
                        "created_at": assessment.created_at.isoformat()
                    }
            
            elif node_type == "document":
                pdf_check = self.db.query(PDFCheck).filter(PDFCheck.id == reference_id).first()
                if pdf_check:
                    return {
                        "filename": pdf_check.filename,
                        "score": pdf_check.score,
                        "is_likely_fake": pdf_check.is_likely_fake,
                        "created_at": pdf_check.created_at.isoformat()
                    }
            
            return None
        except Exception:
            return None

    async def auto_link_fraud_cases(self) -> Dict[str, int]:
        """Automatically link related fraud cases into chains"""
        chains_created = 0
        links_added = 0
        
        # Get all tips and assessments that aren't already in chains
        existing_tip_nodes = self.db.query(FraudChainNode.reference_id).filter(
            FraudChainNode.node_type == "tip"
        ).all()
        existing_tip_ids = {node.reference_id for node in existing_tip_nodes}
        
        tips_with_assessments = self.db.query(Tip, Assessment).join(
            Assessment, Tip.id == Assessment.tip_id
        ).filter(
            ~Tip.id.in_(existing_tip_ids)
        ).all()
        
        # Group by similar characteristics
        stock_symbol_groups = {}
        high_risk_groups = []
        
        for tip, assessment in tips_with_assessments:
            # Group by stock symbols
            if assessment.stock_symbols:
                for symbol in assessment.stock_symbols:
                    if symbol not in stock_symbol_groups:
                        stock_symbol_groups[symbol] = []
                    stock_symbol_groups[symbol].append((tip, assessment))
            
            # Group high-risk cases
            if assessment.level == "High" and assessment.score >= 80:
                high_risk_groups.append((tip, assessment))
        
        # Create chains for stock symbol groups
        for symbol, cases in stock_symbol_groups.items():
            if len(cases) >= 2:  # Only create chain if multiple cases
                chain = await self._create_chain_for_cases(
                    cases, 
                    f"Stock Symbol Chain: {symbol}",
                    f"Fraud cases involving stock symbol {symbol}"
                )
                if chain:
                    chains_created += 1
                    links_added += len(cases)
        
        # Create chain for high-risk cases without specific stock symbols
        unlinked_high_risk = []
        for tip, assessment in high_risk_groups:
            if not assessment.stock_symbols:
                unlinked_high_risk.append((tip, assessment))
        
        if len(unlinked_high_risk) >= 3:  # Create chain for multiple high-risk cases
            chain = await self._create_chain_for_cases(
                unlinked_high_risk,
                "High-Risk Fraud Pattern",
                "Collection of high-risk fraud cases with similar patterns"
            )
            if chain:
                chains_created += 1
                links_added += len(unlinked_high_risk)
        
        return {
            "chains_created": chains_created,
            "links_added": links_added
        }

    async def upsert_entity_into_chain(
        self,
        *,
        entity_type: str,
        reference_id: str,
        label: Optional[str] = None,
        chain_id: Optional[str] = None,
        create_new_chain: bool = True,
    ) -> Dict[str, Any]:
        """Upsert a specific entity as a node into a fraud chain.

        - If chain_id is provided, add the node to that chain.
        - Else, if the entity already exists in a chain, return that.
        - Else, create a new chain when allowed.
        - For convenience, create minimal edges to related entities when obvious.
        """
        try:
            entity_type = (entity_type or '').strip().lower()
            if entity_type not in {"tip", "assessment", "document"}:
                return {"error": f"Unsupported entity_type: {entity_type}"}

            # If node already exists anywhere, return its chain
            existing_node = (
                self.db.query(FraudChainNode)
                .filter(
                    and_(
                        FraudChainNode.node_type == entity_type,
                        FraudChainNode.reference_id == reference_id,
                    )
                )
                .first()
            )
            if existing_node:
                return {"chain_id": existing_node.chain_id, "node_id": existing_node.id, "created": False}

            # Resolve or create target chain
            target_chain: Optional[FraudChain] = None
            if chain_id:
                target_chain = self.db.query(FraudChain).filter(FraudChain.id == chain_id).first()
            if not target_chain and create_new_chain:
                # Derive basic label
                default_name = f"{entity_type.capitalize()} Case"
                target_chain = FraudChain(name=default_name, status="active")
                self.db.add(target_chain)
                self.db.flush()

            if not target_chain:
                return {"error": "Chain not found and create_new_chain is False"}

            # Create the node
            node_label = label
            node_metadata: Dict[str, Any] = {}

            if entity_type == "tip":
                tip = self.db.query(Tip).filter(Tip.id == reference_id).first()
                if tip:
                    node_label = node_label or (tip.message[:50] + ("..." if len(tip.message) > 50 else ""))
                    node_metadata.update({"source": tip.source, "created_at": tip.created_at.isoformat()})
            elif entity_type == "assessment":
                assessment = self.db.query(Assessment).filter(Assessment.id == reference_id).first()
                if assessment:
                    node_label = node_label or f"Risk: {assessment.level} ({assessment.score}%)"
                    node_metadata.update({
                        "level": assessment.level,
                        "score": assessment.score,
                        "stock_symbols": assessment.stock_symbols,
                    })
            elif entity_type == "document":
                pdf = self.db.query(PDFCheck).filter(PDFCheck.id == reference_id).first()
                if pdf:
                    node_label = node_label or f"Document: {pdf.filename}"
                    node_metadata.update({
                        "filename": pdf.filename,
                        "score": pdf.score,
                        "is_likely_fake": pdf.is_likely_fake,
                    })

            node = FraudChainNode(
                chain_id=target_chain.id,
                node_type=entity_type,
                reference_id=reference_id,
                label=node_label,
                node_metadata=node_metadata,
                position_x=150,
                position_y=150,
            )
            self.db.add(node)
            self.db.flush()

            # Minimal convenience edges
            if entity_type == "assessment":
                # Link assessment to its tip if exists
                assessment = self.db.query(Assessment).filter(Assessment.id == reference_id).first()
                if assessment and assessment.tip_id:
                    tip_node = (
                        self.db.query(FraudChainNode)
                        .filter(
                            and_(
                                FraudChainNode.chain_id == target_chain.id,
                                FraudChainNode.node_type == "tip",
                                FraudChainNode.reference_id == assessment.tip_id,
                            )
                        )
                        .first()
                    )
                    if not tip_node:
                        # Create the tip node as well
                        tip = self.db.query(Tip).filter(Tip.id == assessment.tip_id).first()
                        if tip:
                            tip_node = FraudChainNode(
                                chain_id=target_chain.id,
                                node_type="tip",
                                reference_id=tip.id,
                                label=f"Tip: {tip.message[:40]}...",
                                position_x=50,
                                position_y=150,
                                node_metadata={"source": tip.source},
                            )
                            self.db.add(tip_node)
                            self.db.flush()
                    if tip_node:
                        edge = FraudChainEdge(
                            chain_id=target_chain.id,
                            from_node_id=tip_node.id,
                            to_node_id=node.id,
                            relationship_type="leads_to",
                            confidence=95,
                            edge_metadata={"auto_generated": True},
                        )
                        self.db.add(edge)

            if entity_type == "tip":
                # Link tip to its assessments (if any)
                assessments = self.db.query(Assessment).filter(Assessment.tip_id == reference_id).all()
                for i, a in enumerate(assessments[:3]):
                    assess_node = FraudChainNode(
                        chain_id=target_chain.id,
                        node_type="assessment",
                        reference_id=a.id,
                        label=f"Risk: {a.level} ({a.score}%)",
                        position_x=150 + (i + 1) * 150,
                        position_y=150,
                        node_metadata={"level": a.level, "score": a.score},
                    )
                    self.db.add(assess_node)
                    self.db.flush()
                    edge = FraudChainEdge(
                        chain_id=target_chain.id,
                        from_node_id=node.id,
                        to_node_id=assess_node.id,
                        relationship_type="leads_to",
                        confidence=95,
                        edge_metadata={"auto_generated": True},
                    )
                    self.db.add(edge)

            self.db.commit()
            return {"chain_id": target_chain.id, "node_id": node.id, "created": True}
        except Exception as e:
            self.db.rollback()
            return {"error": str(e)}

    async def _create_chain_for_cases(self, cases: List[tuple], name: str, description: str) -> Optional[FraudChain]:
        """Create a fraud chain for a group of related cases"""
        try:
            # Create the chain
            chain = FraudChain(
                name=name,
                description=description,
                status="active"
            )
            self.db.add(chain)
            self.db.flush()  # Get the chain ID

            nodes: List[FraudChainNode] = []

            # Create nodes for each case
            for i, (tip, assessment) in enumerate(cases):
                # Create tip node
                tip_node = FraudChainNode(
                    chain_id=chain.id,
                    node_type="tip",
                    reference_id=tip.id,
                    label=f"Tip: {tip.message[:50]}...",
                    position_x=100 + (i * 200),
                    position_y=100,
                    node_metadata={
                        "source": tip.source,
                        "created_at": tip.created_at.isoformat(),
                    },
                )
                self.db.add(tip_node)
                nodes.append(tip_node)

                # Create assessment node
                assessment_node = FraudChainNode(
                    chain_id=chain.id,
                    node_type="assessment",
                    reference_id=assessment.id,
                    label=f"Risk: {assessment.level} ({assessment.score}%)",
                    position_x=100 + (i * 200),
                    position_y=200,
                    node_metadata={
                        "level": assessment.level,
                        "score": assessment.score,
                        "stock_symbols": assessment.stock_symbols,
                    },
                )
                self.db.add(assessment_node)
                nodes.append(assessment_node)

            # Flush to get node IDs
            self.db.flush()

            # Create edges after nodes have IDs (tip -> assessment)
            for i in range(0, len(nodes) - 1, 2):
                edge = FraudChainEdge(
                    chain_id=chain.id,
                    from_node_id=nodes[i].id,
                    to_node_id=nodes[i + 1].id,
                    relationship_type="leads_to",
                    confidence=100,
                    edge_metadata={"auto_generated": True},
                )
                self.db.add(edge)

            # Create edges between similar cases (tip -> next tip)
            for i in range(0, len(nodes) - 2, 2):
                if i + 2 < len(nodes):
                    similarity_edge = FraudChainEdge(
                        chain_id=chain.id,
                        from_node_id=nodes[i].id,
                        to_node_id=nodes[i + 2].id,
                        relationship_type="similar_pattern",
                        confidence=75,
                        edge_metadata={
                            "auto_generated": True,
                            "similarity_type": "content_pattern",
                        },
                    )
                    self.db.add(similarity_edge)

            self.db.commit()
            return chain

        except Exception as e:
            self.db.rollback()
            print(f"Error creating fraud chain: {e}")
            return None

    async def export_chain_json(self, chain_id: str) -> Dict[str, Any]:
        """Export fraud chain as JSON"""
        chain_data = await self.get_fraud_chain_by_id(chain_id)
        if not chain_data:
            return {"error": "Chain not found"}

        return {
            "export_format": "json",
            "export_timestamp": datetime.utcnow().isoformat(),
            "chain_data": chain_data,
        }

    async def export_chain_csv(self, chain_id: str) -> StreamingResponse:
        """Export fraud chain as CSV (nodes and edges flat lists)."""
        chain_data = await self.get_fraud_chain_by_id(chain_id)
        if not chain_data:
            return StreamingResponse(io.StringIO("Error: Chain not found"), media_type="text/csv")

        output = io.StringIO()
        writer = csv.writer(output)
        # Nodes section
        writer.writerow(["NODES"])
        writer.writerow(["id", "node_type", "reference_id", "label", "position_x", "position_y", "created_at"])
        for node in chain_data.get("nodes", []):
            writer.writerow([
                node.get("id", ""),
                node.get("node_type", ""),
                node.get("reference_id", ""),
                node.get("label", ""),
                node.get("position_x", ""),
                node.get("position_y", ""),
                node.get("created_at", ""),
            ])
        # Edges section
        writer.writerow(["EDGES"])
        writer.writerow(["id", "from_node_id", "to_node_id", "relationship_type", "confidence", "created_at"])
        for edge in chain_data.get("edges", []):
            writer.writerow([
                edge.get("id", ""),
                edge.get("from_node_id", ""),
                edge.get("to_node_id", ""),
                edge.get("relationship_type", ""),
                edge.get("confidence", ""),
                edge.get("created_at", ""),
            ])

        csv_data = output.getvalue()
        output.close()
        headers = {"Content-Disposition": f"attachment; filename=chain_{chain_id}.csv"}
        return StreamingResponse(iter([csv_data]), media_type="text/csv", headers=headers)

    async def _create_sample_chain_structure(self, chain_id: str, cases: List[tuple], theme: str):
        """Create a sample chain structure with nodes and edges"""
        nodes = []
        
        for i, (tip, assessment) in enumerate(cases):
            # Create tip node
            tip_node = FraudChainNode(
                chain_id=chain_id,
                node_type="tip",
                reference_id=tip.id,
                label=f"{theme} Tip #{i+1}",
                position_x=150 + (i * 250),
                position_y=100,
                node_metadata={
                    "theme": theme,
                    "sequence": i + 1,
                    "source": tip.source
                }
            )
            self.db.add(tip_node)
            nodes.append(tip_node)
            
            # Create assessment node
            assessment_node = FraudChainNode(
                chain_id=chain_id,
                node_type="assessment",
                reference_id=assessment.id,
                label=f"Risk Assessment: {assessment.level}",
                position_x=150 + (i * 250),
                position_y=250,
                node_metadata={
                    "risk_level": assessment.level,
                    "risk_score": assessment.score
                }
            )
            self.db.add(assessment_node)
            nodes.append(assessment_node)
        
        self.db.flush()  # Get node IDs
        
        # Create edges
        for i in range(0, len(nodes) - 1, 2):  # Connect tip to assessment pairs
            edge = FraudChainEdge(
                chain_id=chain_id,
                from_node_id=nodes[i].id,
                to_node_id=nodes[i + 1].id,
                relationship_type="leads_to",
                confidence=95,
                edge_metadata={"connection_type": "tip_to_assessment"}
            )
            self.db.add(edge)
            
            # Connect to next tip if exists
            if i + 2 < len(nodes):
                progression_edge = FraudChainEdge(
                    chain_id=chain_id,
                    from_node_id=nodes[i + 1].id,  # Current assessment
                    to_node_id=nodes[i + 2].id,    # Next tip
                    relationship_type="escalates_to",
                    confidence=80,
                    edge_metadata={"connection_type": "progression"}
                )
                self.db.add(progression_edge)

        self.db.commit()

    async def get_relations_subgraph(self, entity_type: str, reference_id: str, depth: int = 1, limit: int = 100) -> Dict[str, Any]:
        """Collect related nodes and edges around a given entity reference using BFS.

        Args:
            entity_type: starting node type (e.g., 'tip', 'assessment', 'document')
            reference_id: reference id to match on starting node(s)
            depth: BFS depth limit (1..3)
            limit: maximum number of nodes to return (<=300)
        """
        # Bound parameters
        depth = max(1, min(depth, 3))
        limit = max(1, min(limit, 300))

        # Find starting nodes across all chains
        start_nodes: List[FraudChainNode] = self.db.query(FraudChainNode).filter(
            and_(
                FraudChainNode.node_type == entity_type,
                FraudChainNode.reference_id == reference_id,
            )
        ).all()

        if not start_nodes:
            return {"nodes": [], "edges": []}

        visited = set()
        collected_nodes: Dict[str, FraudChainNode] = {}
        collected_edges: Dict[str, FraudChainEdge] = {}

        from collections import deque
        q = deque()
        for n in start_nodes:
            nid = str(n.id)
            q.append((n.id, depth))
            visited.add(nid)
            collected_nodes[nid] = n

        while q and len(collected_nodes) < limit:
            current_id, rem = q.popleft()
            if rem <= 0:
                continue

            adj_edges: List[FraudChainEdge] = self.db.query(FraudChainEdge).filter(
                or_(
                    FraudChainEdge.from_node_id == current_id,
                    FraudChainEdge.to_node_id == current_id,
                )
            ).all()

            for e in adj_edges:
                collected_edges[str(e.id)] = e
                neighbor_id = e.to_node_id if e.from_node_id == current_id else e.from_node_id
                nid = str(neighbor_id)
                if nid not in visited and len(collected_nodes) < limit:
                    neighbor = self.db.query(FraudChainNode).filter(FraudChainNode.id == neighbor_id).first()
                    if neighbor:
                        visited.add(nid)
                        collected_nodes[nid] = neighbor
                        q.append((neighbor.id, rem - 1))

        # Serialize
        nodes_out: List[Dict[str, Any]] = []
        for node in collected_nodes.values():
            try:
                nodes_out.append({
                    "id": node.id,
                    "node_type": node.node_type,
                    "reference_id": node.reference_id,
                    "label": node.label,
                    "metadata": node.node_metadata or {},
                    "position_x": node.position_x,
                    "position_y": node.position_y,
                    "created_at": node.created_at,
                })
            except Exception:
                continue

        edges_out: List[Dict[str, Any]] = []
        for edge in collected_edges.values():
            try:
                edges_out.append({
                    "id": edge.id,
                    "from_node_id": edge.from_node_id,
                    "to_node_id": edge.to_node_id,
                    "relationship_type": edge.relationship_type,
                    "confidence": edge.confidence,
                    "metadata": edge.edge_metadata or {},
                    "created_at": edge.created_at,
                })
            except Exception:
                continue

        return {"nodes": nodes_out[:limit], "edges": edges_out}

    async def search_nodes(
        self,
        *,
        query: str,
        chain_id: Optional[str] = None,
        limit_per_chain: int = 200,
    ) -> Dict[str, Any]:
        """Search nodes by label, type, reference_id, or metadata (case-insensitive).

        Returns grouped reference_ids per chain for precise client-side highlighting.
        """
        import time

        t0 = time.time()
        q = (query or "").strip().lower()
        if not q:
            return {"total": 0, "took_ms": int((time.time() - t0) * 1000), "used_backend": "sqlite_fallback", "results": []}

        try:
            base_query = self.db.query(FraudChainNode)
            if chain_id:
                base_query = base_query.filter(FraudChainNode.chain_id == chain_id)

            nodes: List[FraudChainNode] = base_query.all()

            grouped: Dict[str, Dict[str, Any]] = {}
            total_matches = 0

            for n in nodes:
                try:
                    label = (n.label or "").lower()
                    ntype = (n.node_type or "").lower()
                    ref_id = (n.reference_id or "").lower()

                    # Serialize metadata to string for coarse matching
                    meta_str = ""
                    try:
                        meta_str = (json.dumps(n.node_metadata or {})).lower()
                    except Exception:
                        meta_str = ""

                    is_match = (
                        (q in label)
                        or (q in ntype)
                        or (q in ref_id)
                        or (q in meta_str)
                    )
                    if not is_match:
                        continue

                    grp = grouped.get(n.chain_id)
                    if not grp:
                        grp = {"chain_id": n.chain_id, "reference_ids": [], "count": 0}
                        grouped[n.chain_id] = grp

                    if len(grp["reference_ids"]) < max(1, limit_per_chain):
                        grp["reference_ids"].append(n.reference_id)
                    grp["count"] += 1
                    total_matches += 1
                except Exception:
                    continue

            took = int((time.time() - t0) * 1000)
            return {
                "total": total_matches,
                "took_ms": took,
                "used_backend": "sqlite_fallback",
                "results": list(grouped.values()),
            }
        except Exception as e:
            return {
                "total": 0,
                "took_ms": int((time.time() - t0) * 1000),
                "used_backend": "sqlite_fallback",
                "results": [],
                "error": str(e),
            }

    async def reset_demo_graph(self) -> Dict[str, Any]:
        """Delete all existing fraud chains, nodes, and edges and recreate a
        minimal, clean demo chain with clickable entities.

        Returns: { message, chain_id, nodes, edges }
        """
        try:
            # Purge in dependency order
            deleted_edges = self.db.query(FraudChainEdge).delete(synchronize_session=False)
            deleted_nodes = self.db.query(FraudChainNode).delete(synchronize_session=False)
            deleted_chains = self.db.query(FraudChain).delete(synchronize_session=False)
            self.db.commit()

            # Create a fresh chain
            chain = FraudChain(
                name="Demo: Clean Example Chain",
                description="Minimal example with Tip -> Assessment, plus Advisor and Document",
                status="active",
            )
            self.db.add(chain)
            self.db.flush()

            # Create referenced domain records
            tip = Tip(message="Demo Tip: suspicious advisor and document", source="demo")
            self.db.add(tip)
            self.db.flush()

            assess = Assessment(
                tip_id=tip.id,
                level="High",
                score=92,
                reasons=["high_return_promise", "language_red_flags"],
                stock_symbols=["DEMOCO"],
                advisor_info={"claimed_sebi_reg": False},
                confidence=90,
            )
            self.db.add(assess)
            self.db.flush()

            # Ensure idempotency for demo PDF record to avoid UNIQUE(file_hash) violation
            existing_pdf = self.db.query(PDFCheck).filter(PDFCheck.file_hash == "demo-contract-001").first()
            if existing_pdf:
                pdf = existing_pdf
            else:
                pdf = PDFCheck(
                    file_hash="demo-contract-001",
                    filename="Demo-Contract-001.pdf",
                    file_size=123456,
                    ocr_text="Demo contract with anomalies",
                    anomalies=["Stamp mismatch"],
                    score=55,
                    is_likely_fake=True,
                    processing_time_ms=900,
                )
                self.db.add(pdf)
                self.db.flush()

            # Graph nodes
            n_tip = FraudChainNode(
                chain_id=chain.id,
                node_type="tip",
                reference_id=tip.id,
                label="Demo Tip",
                position_x=120,
                position_y=140,
                node_metadata={"source": tip.source},
            )
            n_assess = FraudChainNode(
                chain_id=chain.id,
                node_type="assessment",
                reference_id=assess.id,
                label=f"Risk: {assess.level} ({assess.score}%)",
                position_x=340,
                position_y=140,
                node_metadata={"level": assess.level, "score": assess.score},
            )
            n_adv = FraudChainNode(
                chain_id=chain.id,
                node_type="advisor",
                reference_id="demo-advisor-1",
                label="Advisor: Demo Advisor",
                position_x=120,
                position_y=300,
                node_metadata={"sebi_status": "pending_verification"},
            )
            n_pdf = FraudChainNode(
                chain_id=chain.id,
                node_type="document",
                reference_id=pdf.id,
                label=pdf.filename,
                position_x=340,
                position_y=300,
                node_metadata={"anomalies": pdf.anomalies},
            )
            self.db.add_all([n_tip, n_assess, n_adv, n_pdf])
            self.db.flush()

            # Graph edges (3 edges)
            e1 = FraudChainEdge(
                chain_id=chain.id,
                from_node_id=n_tip.id,
                to_node_id=n_assess.id,
                relationship_type="leads_to",
                confidence=98,
                edge_metadata={"auto": True},
            )
            e2 = FraudChainEdge(
                chain_id=chain.id,
                from_node_id=n_tip.id,
                to_node_id=n_adv.id,
                relationship_type="mentions",
                confidence=85,
                edge_metadata={"auto": True},
            )
            e3 = FraudChainEdge(
                chain_id=chain.id,
                from_node_id=n_tip.id,
                to_node_id=n_pdf.id,
                relationship_type="references",
                confidence=80,
                edge_metadata={"auto": True},
            )
            self.db.add_all([e1, e2, e3])
            self.db.commit()

            return {
                "message": "Demo graph reset successfully",
                "deleted": {"chains": deleted_chains, "nodes": deleted_nodes, "edges": deleted_edges},
                "chain_id": chain.id,
                "nodes": 4,
                "edges": 3,
            }
        except Exception as e:
            self.db.rollback()
            return {"error": str(e)}