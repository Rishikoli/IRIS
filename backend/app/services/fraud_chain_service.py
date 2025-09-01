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
            node_count = self.db.query(func.count(FraudChainNode.id)).filter(FraudChainNode.chain_id == chain.id).scalar()
            edge_count = self.db.query(func.count(FraudChainEdge.id)).filter(FraudChainEdge.chain_id == chain.id).scalar()
            
            result.append({
                "id": chain.id,
                "name": chain.name,
                "description": chain.description,
                "status": chain.status,
                "node_count": node_count,
                "edge_count": edge_count,
                "created_at": chain.created_at,
                "updated_at": chain.updated_at
            })
        
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
            
            nodes = []
            
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
                        "created_at": tip.created_at.isoformat()
                    }
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
                        "stock_symbols": assessment.stock_symbols
                    }
                )
                self.db.add(assessment_node)
                nodes.append(assessment_node)
            
            # Flush to get node IDs
            self.db.flush()
            
            # Create edges after nodes have IDs
            for i in range(0, len(nodes) - 1, 2):  # Step by 2 since we have tip-assessment pairs
                # Create edge from tip to assessment
                edge = FraudChainEdge(
                    chain_id=chain.id,
                    from_node_id=nodes[i].id,
                    to_node_id=nodes[i + 1].id,
                    relationship_type="leads_to",
                    confidence=100,
                    edge_metadata={"auto_generated": True}
                )
                self.db.add(edge)
            
            # Create edges between similar cases
            for i in range(0, len(nodes) - 2, 2):  # Step by 2 since we have tip-assessment pairs
                if i + 2 < len(nodes):
                    similarity_edge = FraudChainEdge(
                        chain_id=chain.id,
                        from_node_id=nodes[i].id,  # Current tip
                        to_node_id=nodes[i + 2].id,  # Next tip
                        relationship_type="similar_pattern",
                        confidence=75,
                        edge_metadata={"auto_generated": True, "similarity_type": "content_pattern"}
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
            "chain_data": chain_data
        }

    async def export_chain_csv(self, chain_id: str) -> StreamingResponse:
        """Export fraud chain as CSV"""
        chain_data = await self.get_fraud_chain_by_id(chain_id)
        if not chain_data:
            return StreamingResponse(
                io.StringIO("Error: Chain not found"),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=error.csv"}
            )
        
        # Create CSV content
        output = io.StringIO()
        
        # Write nodes
        output.write("=== NODES ===\n")
        writer = csv.writer(output)
        writer.writerow(["ID", "Type", "Label", "Reference ID", "Position X", "Position Y", "Created At"])
        
        for node in chain_data["nodes"]:
            writer.writerow([
                node["id"],
                node["node_type"],
                node["label"] or "",
                node["reference_id"],
                node["position_x"] or "",
                node["position_y"] or "",
                node["created_at"]
            ])
        
        output.write("\n=== EDGES ===\n")
        writer.writerow(["ID", "From Node", "To Node", "Relationship", "Confidence", "Created At"])
        
        for edge in chain_data["edges"]:
            writer.writerow([
                edge["id"],
                edge["from_node_id"],
                edge["to_node_id"],
                edge["relationship_type"],
                edge["confidence"],
                edge["created_at"]
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=fraud_chain_{chain_id}.csv"}
        )

    async def create_sample_fraud_chains(self) -> Dict[str, Any]:
        """Create sample fraud chain data for demonstration"""
        try:
            # Get some existing tips and assessments
            tips_with_assessments = self.db.query(Tip, Assessment).join(
                Assessment, Tip.id == Assessment.tip_id
            ).limit(6).all()
            
            if len(tips_with_assessments) < 3:
                return {"error": "Not enough data to create sample chains"}
            
            # Create first sample chain - Stock manipulation scheme
            chain1 = FraudChain(
                name="ABC Corp Stock Manipulation",
                description="Coordinated pump-and-dump scheme targeting ABC Corp shares",
                status="investigating"
            )
            self.db.add(chain1)
            self.db.flush()
            
            # Create nodes and edges for chain1
            if len(tips_with_assessments) >= 3:
                await self._create_sample_chain_structure(chain1.id, tips_with_assessments[:3], "ABC")
            
            # Create second sample chain - Fake advisor scheme
            chain2 = FraudChain(
                name="Fake SEBI Advisor Network",
                description="Network of fraudsters impersonating registered SEBI advisors",
                status="active"
            )
            self.db.add(chain2)
            self.db.flush()
            
            if len(tips_with_assessments) >= 6:
                await self._create_sample_chain_structure(chain2.id, tips_with_assessments[3:6], "ADVISOR")
            
            self.db.commit()
            
            return {
                "message": "Sample fraud chains created successfully",
                "chains": [
                    {"id": chain1.id, "name": chain1.name},
                    {"id": chain2.id, "name": chain2.name}
                ]
            }
            
        except Exception as e:
            self.db.rollback()
            return {"error": f"Failed to create sample chains: {str(e)}"}

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