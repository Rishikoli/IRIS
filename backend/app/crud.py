from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from app.models import Tip, Assessment, PDFCheck, HeatmapBucket, Review
from typing import List, Optional
from datetime import date, datetime, timedelta

# Tip CRUD operations
def create_tip(db: Session, message: str, source: str = "manual", submitter_id: Optional[str] = None) -> Tip:
    tip = Tip(message=message, source=source, submitter_id=submitter_id)
    db.add(tip)
    db.commit()
    db.refresh(tip)
    return tip

def get_tip(db: Session, tip_id: str) -> Optional[Tip]:
    return db.query(Tip).filter(Tip.id == tip_id).first()

def get_tips(db: Session, skip: int = 0, limit: int = 100) -> List[Tip]:
    return db.query(Tip).offset(skip).limit(limit).all()

def delete_tip(db: Session, tip_id: str) -> bool:
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if tip:
        db.delete(tip)
        db.commit()
        return True
    return False

# Assessment CRUD operations
def create_assessment(
    db: Session, 
    tip_id: str, 
    level: str, 
    score: int, 
    reasons: List[str],
    stock_symbols: List[str] = None,
    advisor_info: dict = None,
    gemini_raw: dict = None,
    confidence: int = None
) -> Assessment:
    assessment = Assessment(
        tip_id=tip_id,
        level=level,
        score=score,
        reasons=reasons,
        stock_symbols=stock_symbols or [],
        advisor_info=advisor_info,
        gemini_raw=gemini_raw,
        confidence=confidence
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

def get_assessment(db: Session, assessment_id: str) -> Optional[Assessment]:
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()

def get_assessments_by_tip(db: Session, tip_id: str) -> List[Assessment]:
    return db.query(Assessment).filter(Assessment.tip_id == tip_id).all()

def get_assessments(db: Session, skip: int = 0, limit: int = 100) -> List[Assessment]:
    return db.query(Assessment).offset(skip).limit(limit).all()

# PDF Check CRUD operations
def create_pdf_check(
    db: Session,
    file_hash: str,
    filename: str,
    file_size: int = None,
    ocr_text: str = None,
    anomalies: List[dict] = None,
    score: int = None,
    is_likely_fake: bool = None,
    processing_time_ms: int = None
) -> PDFCheck:
    pdf_check = PDFCheck(
        file_hash=file_hash,
        filename=filename,
        file_size=file_size,
        ocr_text=ocr_text,
        anomalies=anomalies or [],
        score=score,
        is_likely_fake=is_likely_fake,
        processing_time_ms=processing_time_ms
    )
    db.add(pdf_check)
    db.commit()
    db.refresh(pdf_check)
    return pdf_check

def get_pdf_check(db: Session, pdf_check_id: str) -> Optional[PDFCheck]:
    return db.query(PDFCheck).filter(PDFCheck.id == pdf_check_id).first()

def get_pdf_check_by_hash(db: Session, file_hash: str) -> Optional[PDFCheck]:
    return db.query(PDFCheck).filter(PDFCheck.file_hash == file_hash).first()

def get_pdf_checks(db: Session, skip: int = 0, limit: int = 100) -> List[PDFCheck]:
    return db.query(PDFCheck).offset(skip).limit(limit).all()

# Heatmap Bucket CRUD operations
def create_heatmap_bucket(
    db: Session,
    dimension: str,
    key: str,
    from_date: date,
    to_date: date,
    total_count: int = 0,
    high_risk_count: int = 0,
    medium_risk_count: int = 0,
    low_risk_count: int = 0
) -> HeatmapBucket:
    bucket = HeatmapBucket(
        dimension=dimension,
        key=key,
        from_date=from_date,
        to_date=to_date,
        total_count=total_count,
        high_risk_count=high_risk_count,
        medium_risk_count=medium_risk_count,
        low_risk_count=low_risk_count
    )
    db.add(bucket)
    db.commit()
    db.refresh(bucket)
    return bucket

def get_heatmap_buckets(
    db: Session,
    dimension: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List[HeatmapBucket]:
    query = db.query(HeatmapBucket).filter(HeatmapBucket.dimension == dimension)
    
    if from_date:
        query = query.filter(HeatmapBucket.from_date >= from_date)
    if to_date:
        query = query.filter(HeatmapBucket.to_date <= to_date)
    
    return query.all()

def update_heatmap_bucket_counts(
    db: Session,
    dimension: str,
    key: str,
    from_date: date,
    to_date: date
) -> HeatmapBucket:
    """Update heatmap bucket counts based on actual assessment data"""
    
    # Get existing bucket or create new one
    bucket = db.query(HeatmapBucket).filter(
        and_(
            HeatmapBucket.dimension == dimension,
            HeatmapBucket.key == key,
            HeatmapBucket.from_date == from_date,
            HeatmapBucket.to_date == to_date
        )
    ).first()
    
    if not bucket:
        bucket = HeatmapBucket(
            dimension=dimension,
            key=key,
            from_date=from_date,
            to_date=to_date
        )
        db.add(bucket)
    
    # Count assessments by risk level in the date range
    # For demo purposes, we'll use a simple mapping based on key names
    # In a real system, this would join with actual sector/region data
    
    # Query assessments in date range
    assessments_query = db.query(Assessment).join(Tip).filter(
        and_(
            func.date(Tip.created_at) >= from_date,
            func.date(Tip.created_at) <= to_date
        )
    )
    
    # For demo, map keys to assessment filters
    # This is simplified - in production you'd have proper sector/region mapping
    if dimension == "sector":
        # Filter by known tickers/keywords appearing in the tip message text
        # Using Tip.message avoids JSON containment dialect issues on SQLite
        if key.lower() in ["technology", "tech"]:
            assessments_query = assessments_query.filter(
                Tip.message.contains("TCS") |
                Tip.message.contains("INFY") |
                Tip.message.contains("WIPRO") |
                Tip.message.contains("TECHM") |
                Tip.message.contains("HCLTECH") |
                Tip.message.contains("tech")
            )
        elif key.lower() in ["banking", "finance"]:
            assessments_query = assessments_query.filter(
                Tip.message.contains("HDFC") |
                Tip.message.contains("ICICI") |
                Tip.message.contains("SBI") |
                Tip.message.contains("KOTAK") |
                Tip.message.contains("AXIS") |
                Tip.message.contains("bank")
            )
        elif key.lower() in ["pharma", "pharmaceutical"]:
            assessments_query = assessments_query.filter(
                Tip.message.contains("CIPLA") |
                Tip.message.contains("DRREDDY") |
                Tip.message.contains("SUNPHARMA") |
                Tip.message.contains("LUPIN") |
                Tip.message.contains("pharma")
            )
    elif dimension == "region":
        # For demo, we'll use a simple distribution
        # In production, this would be based on user location or other regional indicators
        pass
    
    assessments = assessments_query.all()
    
    # Count by risk level
    high_count = len([a for a in assessments if a.level == "High"])
    medium_count = len([a for a in assessments if a.level == "Medium"])
    low_count = len([a for a in assessments if a.level == "Low"])
    total_count = len(assessments)
    
    # Update bucket counts
    bucket.total_count = total_count
    bucket.high_risk_count = high_count
    bucket.medium_risk_count = medium_count
    bucket.low_risk_count = low_count
    bucket.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(bucket)
    return bucket

def aggregate_heatmap_data(
    db: Session,
    dimension: str,
    period: str = "weekly",
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List[dict]:
    """Aggregate fraud data for heatmap visualization"""
    
    if not from_date:
        from_date = date.today() - timedelta(days=30)
    if not to_date:
        to_date = date.today()
    # Guard against invalid ranges
    if from_date > to_date:
        return []
    
    # Define keys for each dimension
    if dimension == "sector":
        keys = ["Technology", "Banking", "Pharma", "Energy", "FMCG", "Auto", "Telecom", "Real Estate"]
    elif dimension == "region":
        keys = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
    else:
        raise ValueError("Invalid dimension. Must be 'sector' or 'region'")
    
    # Calculate date ranges based on period
    date_ranges = []
    current_date = from_date
    
    while current_date <= to_date:
        # Start of this bucket
        range_start = current_date
        
        if period == "daily":
            range_end = range_start
            # advance to next day
            current_date = range_end + timedelta(days=1)
        elif period == "weekly":
            range_end = min(range_start + timedelta(days=6), to_date)
            # advance to the day after this range
            current_date = range_end + timedelta(days=1)
        elif period == "monthly":
            # Simple monthly approximation (30-day buckets)
            range_end = min(range_start + timedelta(days=29), to_date)
            current_date = range_end + timedelta(days=1)
        else:
            raise ValueError("Invalid period. Must be 'daily', 'weekly', or 'monthly'")
        
        # Append the computed (start, end) inclusive range
        date_ranges.append((range_start, range_end))
    
    # Update buckets for each key and date range
    result = []
    for key in keys:
        for range_start, range_end in date_ranges:
            bucket = update_heatmap_bucket_counts(db, dimension, key, range_start, range_end)
            result.append({
                "dimension": dimension,
                "key": key,
                "from_date": range_start.isoformat(),
                "to_date": range_end.isoformat(),
                "total_count": bucket.total_count,
                "high_risk_count": bucket.high_risk_count,
                "medium_risk_count": bucket.medium_risk_count,
                "low_risk_count": bucket.low_risk_count,
                "risk_score": calculate_risk_score(bucket.high_risk_count, bucket.medium_risk_count, bucket.low_risk_count),
                "last_updated": bucket.last_updated.isoformat()
            })
    
    return result

def calculate_risk_score(high_count: int, medium_count: int, low_count: int) -> float:
    """Calculate a risk score from 0-100 based on risk level counts"""
    total = high_count + medium_count + low_count
    if total == 0:
        return 0.0
    
    # Weighted score: High=3, Medium=2, Low=1
    weighted_sum = (high_count * 3) + (medium_count * 2) + (low_count * 1)
    max_possible = total * 3
    
    return round((weighted_sum / max_possible) * 100, 2)

def generate_realtime_fraud_cases(db: Session, count: int = 20) -> List[Assessment]:
    """Generate realistic fraud cases for real-time demonstration"""
    import random
    from datetime import datetime, timedelta
    
    # Sample fraud messages by sector
    fraud_templates = {
        "Technology": [
            "🚀 URGENT: TCS stock will jump 500% tomorrow! Inside information from CEO meeting. Buy now before it's too late!",
            "💰 INFY guaranteed returns of 1000% in 30 days. Secret algorithm trading. Limited spots available!",
            "⚡ Tech sector insider tip: Major announcement coming. Buy WIPRO, TECHM now for massive gains!",
            "🔥 AI revolution stock tip: Buy these tech stocks now for guaranteed 10x returns in 1 week!"
        ],
        "Banking": [
            "💸 HDFC Bank merger news leaked! Stock will double overnight. Buy maximum quantity now!",
            "🏦 Banking sector crash coming! Sell all ICICI, SBI immediately. Save your money!",
            "💳 Secret RBI meeting leaked: New banking rules will make these stocks skyrocket!",
            "🎯 Guaranteed banking stock returns: 800% profit in KOTAK, AXIS in 15 days only!"
        ],
        "Pharma": [
            "💊 COVID vaccine breakthrough! CIPLA stock will explode 2000% this week!",
            "🧬 Pharma insider: FDA approval coming for DRREDDY. Buy before announcement!",
            "⚕️ Medical breakthrough leaked: These pharma stocks guaranteed 15x returns!",
            "🩺 Healthcare revolution: Secret drug approval will make you millionaire overnight!"
        ],
        "Energy": [
            "⚡ Oil prices manipulation exposed! Energy stocks will crash 90% tomorrow!",
            "🛢️ Secret government contract: ONGC, NTPC will give 1500% returns this month!",
            "🔋 Green energy revolution: These stocks guaranteed to make you rich in 7 days!",
            "⛽ Fuel price insider information: Buy these energy stocks for massive profits!"
        ],
        "FMCG": [
            "🛒 FMCG sector insider tip: HUL, ITC will give 600% returns after secret product launch!",
            "🥤 Consumer goods revolution: These FMCG stocks guaranteed 10x in 2 weeks!",
            "🍪 Secret recipe leaked: Food company stocks will explode 800% overnight!",
            "🧴 FMCG merger news: Buy maximum before announcement for guaranteed profits!"
        ],
        "Auto": [
            "🚗 Auto sector breakthrough: TATA Motors will give 2000% returns after EV announcement!",
            "🏍️ Secret government policy: Auto stocks guaranteed to skyrocket 1500%!",
            "🚙 Electric vehicle revolution: These auto stocks will make you millionaire!",
            "⚡ Auto insider tip: Buy BAJAJ, HERO before massive announcement tomorrow!"
        ],
        "Telecom": [
            "📱 5G revolution leaked: Telecom stocks guaranteed 1000% returns this week!",
            "📡 Secret spectrum auction results: BHARTI, JIO will explode overnight!",
            "📞 Telecom merger insider news: These stocks will give 800% profits!",
            "🌐 Internet revolution coming: Guaranteed telecom stock profits in 5 days!"
        ],
        "Real Estate": [
            "🏠 Real estate crash coming! Sell all property stocks immediately!",
            "🏢 Secret smart city project: These real estate stocks guaranteed 1200% returns!",
            "🏗️ Construction boom leaked: Buy DLF, GODREJ for massive overnight profits!",
            "🏘️ Property insider tip: Real estate revolution will make you rich in 10 days!"
        ]
    }
    
    # Regional distribution for realistic data
    regions = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
    
    generated_cases = []
    
    for i in range(count):
        # Random sector and message
        sector = random.choice(list(fraud_templates.keys()))
        message = random.choice(fraud_templates[sector])
        
        # Random region
        region = random.choice(regions)
        
        # Create tip with regional context
        tip = create_tip(
            db=db,
            message=f"[{region}] {message}",
            source="realtime_generator",
            submitter_id=f"user_{random.randint(1000, 9999)}"
        )
        
        # Generate realistic assessment
        # Higher chance of high risk for obvious fraud patterns
        risk_weights = [0.6, 0.25, 0.15]  # High, Medium, Low
        risk_level = random.choices(["High", "Medium", "Low"], weights=risk_weights)[0]
        
        # Score based on risk level
        if risk_level == "High":
            score = random.randint(70, 95)
        elif risk_level == "Medium":
            score = random.randint(40, 69)
        else:
            score = random.randint(10, 39)
        
        # Generate realistic reasons
        reasons = []
        if "guaranteed" in message.lower() or "%" in message:
            reasons.append("Unrealistic return promises detected")
        if "urgent" in message.lower() or "immediately" in message.lower():
            reasons.append("High-pressure tactics identified")
        if "secret" in message.lower() or "insider" in message.lower():
            reasons.append("Insider trading claims")
        if "🚀" in message or "💰" in message or "🔥" in message:
            reasons.append("Emotional manipulation through emojis")
        
        if not reasons:
            reasons = ["Suspicious investment advice pattern"]
        
        # Extract stock symbols from sector
        stock_symbols = []
        if sector == "Technology":
            stock_symbols = random.sample(["TCS", "INFY", "WIPRO", "TECHM", "HCLTECH"], random.randint(1, 3))
        elif sector == "Banking":
            stock_symbols = random.sample(["HDFC", "ICICI", "SBI", "KOTAK", "AXIS"], random.randint(1, 2))
        elif sector == "Pharma":
            stock_symbols = random.sample(["CIPLA", "DRREDDY", "SUNPHARMA", "LUPIN"], random.randint(1, 2))
        
        # Create assessment
        assessment = create_assessment(
            db=db,
            tip_id=tip.id,
            level=risk_level,
            score=score,
            reasons=reasons,
            stock_symbols=stock_symbols,
            confidence=random.randint(75, 95)
        )
        
        generated_cases.append(assessment)
        
        # Add some time variation to make it realistic
        if i % 5 == 0:
            # Backdate some entries to create historical data
            backdated_time = datetime.utcnow() - timedelta(
                hours=random.randint(1, 72),
                minutes=random.randint(0, 59)
            )
            tip.created_at = backdated_time
            assessment.created_at = backdated_time
            db.commit()
    
    return generated_cases

def get_heatmap_drill_down_data(
    db: Session,
    dimension: str,
    key: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> dict:
    """Get detailed drill-down data for a specific heatmap cell"""
    
    if not from_date:
        from_date = date.today() - timedelta(days=7)
    if not to_date:
        to_date = date.today()
    
    # Get assessments for this dimension/key combination
    assessments_query = db.query(Assessment).join(Tip).filter(
        and_(
            func.date(Tip.created_at) >= from_date,
            func.date(Tip.created_at) <= to_date
        )
    )
    
    # Filter by dimension/key
    if dimension == "sector":
        # Map sector to stock symbols or message content
        sector_mappings = {
            "Technology": ["TCS", "INFY", "WIPRO", "TECHM", "HCLTECH"],
            "Banking": ["HDFC", "ICICI", "SBI", "KOTAK", "AXIS"],
            "Pharma": ["CIPLA", "DRREDDY", "SUNPHARMA", "LUPIN"],
            "Energy": ["ONGC", "NTPC", "POWERGRID"],
            "FMCG": ["HUL", "ITC", "NESTLEIND"],
            "Auto": ["TATAMOTORS", "BAJAJ", "HERO", "MARUTI"],
            "Telecom": ["BHARTI", "JIO", "IDEA"],
            "Real Estate": ["DLF", "GODREJ", "OBEROI"]
        }
        
        if key in sector_mappings:
            symbols = sector_mappings[key]
            symbol_conditions = [Assessment.stock_symbols.contains(f'"{symbol}"') for symbol in symbols]
            if symbol_conditions:
                from sqlalchemy import or_
                assessments_query = assessments_query.filter(or_(*symbol_conditions))
    
    elif dimension == "region":
        # Filter by region mentioned in tip message
        assessments_query = assessments_query.filter(
            Tip.message.contains(f"[{key}]")
        )
    
    assessments = assessments_query.all()
    
    # Prepare detailed case data
    cases = []
    for assessment in assessments:
        cases.append({
            "id": assessment.id,
            "tip_id": assessment.tip_id,
            "message": assessment.tip.message[:100] + "..." if len(assessment.tip.message) > 100 else assessment.tip.message,
            "risk_level": assessment.level,
            "risk_score": assessment.score,
            "reasons": assessment.reasons,
            "stock_symbols": assessment.stock_symbols,
            "confidence": assessment.confidence,
            "created_at": assessment.created_at.isoformat(),
            "source": assessment.tip.source
        })
    
    # Calculate statistics
    total_cases = len(cases)
    high_risk_cases = len([c for c in cases if c["risk_level"] == "High"])
    medium_risk_cases = len([c for c in cases if c["risk_level"] == "Medium"])
    low_risk_cases = len([c for c in cases if c["risk_level"] == "Low"])
    
    avg_score = sum(c["risk_score"] for c in cases) / total_cases if total_cases > 0 else 0
    
    return {
        "dimension": dimension,
        "key": key,
        "date_range": {
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat()
        },
        "statistics": {
            "total_cases": total_cases,
            "high_risk_cases": high_risk_cases,
            "medium_risk_cases": medium_risk_cases,
            "low_risk_cases": low_risk_cases,
            "average_risk_score": round(avg_score, 2)
        },
        "cases": cases[:20],  # Limit to 20 most recent cases
        "has_more": total_cases > 20
    }

# Review CRUD operations
def create_review(
    db: Session,
    case_id: str,
    case_type: str,
    reviewer_id: str,
    ai_decision: dict,
    decision: str,
    notes: str = None,
    human_decision: dict = None,
    ai_confidence: int = None,
    priority: str = "medium"
) -> Review:
    """Create a new review record"""
    review = Review(
        case_id=case_id,
        case_type=case_type,
        reviewer_id=reviewer_id,
        ai_decision=ai_decision,
        decision=decision,
        notes=notes,
        human_decision=human_decision,
        ai_confidence=ai_confidence,
        priority=priority,
        status="pending" if decision in ["needs_review", "needs_more_info"] else "completed"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def get_review(db: Session, review_id: str) -> Optional[Review]:
    """Get a specific review by ID"""
    return db.query(Review).filter(Review.id == review_id).first()

def get_reviews(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: str = None,
    case_type: str = None,
    priority: str = None
) -> List[Review]:
    """Get reviews with optional filtering"""
    query = db.query(Review)
    
    if status:
        query = query.filter(Review.status == status)
    if case_type:
        query = query.filter(Review.case_type == case_type)
    if priority:
        query = query.filter(Review.priority == priority)
    
    return query.order_by(Review.created_at.desc()).offset(skip).limit(limit).all()

def get_review_queue(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    sort_by: str = "priority"
) -> List[dict]:
    """Get review queue with case details for human reviewers"""
    
    # Get pending reviews sorted by priority and confidence
    reviews_query = db.query(Review).filter(Review.status == "pending")
    
    if sort_by == "priority":
        # Custom priority ordering: high -> medium -> low
        reviews_query = reviews_query.order_by(
            case(
                (Review.priority == "high", 1),
                (Review.priority == "medium", 2),
                (Review.priority == "low", 3),
                else_=4
            ),
            Review.created_at.desc()
        )
    elif sort_by == "confidence":
        # Sort by AI confidence (lowest first - needs most review)
        reviews_query = reviews_query.order_by(Review.ai_confidence.asc(), Review.created_at.desc())
    elif sort_by == "date":
        reviews_query = reviews_query.order_by(Review.created_at.desc())
    
    reviews = reviews_query.offset(skip).limit(limit).all()
    
    # Enrich with case details
    queue_items = []
    for review in reviews:
        case_details = None
        
        if review.case_type == "assessment":
            assessment = get_assessment(db, review.case_id)
            if assessment:
                tip = get_tip(db, assessment.tip_id)
                case_details = {
                    "type": "assessment",
                    "assessment_id": assessment.id,
                    "tip_message": tip.message if tip else "Unknown tip",
                    "risk_level": assessment.level,
                    "risk_score": assessment.score,
                    "reasons": assessment.reasons,
                    "stock_symbols": assessment.stock_symbols,
                    "created_at": assessment.created_at.isoformat()
                }
        elif review.case_type == "pdf_check":
            pdf_check = get_pdf_check(db, review.case_id)
            if pdf_check:
                case_details = {
                    "type": "pdf_check",
                    "pdf_check_id": pdf_check.id,
                    "filename": pdf_check.filename,
                    "authenticity_score": pdf_check.score,
                    "is_likely_fake": pdf_check.is_likely_fake,
                    "anomalies": pdf_check.anomalies,
                    "created_at": pdf_check.created_at.isoformat()
                }
        
        # If no case details found, create a fallback for testing/orphaned reviews
        if not case_details:
            case_details = {
                "type": review.case_type,
                "case_id": review.case_id,
                "message": "Case details not found - may be a test case or orphaned review",
                "created_at": review.created_at.isoformat()
            }
        
        queue_items.append({
            "review_id": review.id,
            "case_id": review.case_id,
            "case_type": review.case_type,
            "priority": review.priority,
            "ai_confidence": review.ai_confidence,
            "ai_decision": review.ai_decision,
            "created_at": review.created_at.isoformat(),
            "case_details": case_details
        })
    
    return queue_items

def update_review_decision(
    db: Session,
    review_id: str,
    decision: str,
    notes: str = None,
    human_decision: dict = None
) -> Optional[Review]:
    """Update review with human decision"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None
    
    review.decision = decision
    review.notes = notes
    review.human_decision = human_decision
    review.status = "completed"
    review.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(review)
    return review

def queue_low_confidence_assessments(db: Session, confidence_threshold: int = 70) -> int:
    """Queue assessments with low AI confidence for human review"""
    
    # Find assessments with low confidence that haven't been reviewed yet
    low_confidence_assessments = db.query(Assessment).filter(
        and_(
            Assessment.confidence < confidence_threshold,
            Assessment.confidence.isnot(None)
        )
    ).all()
    
    queued_count = 0
    
    for assessment in low_confidence_assessments:
        # Check if already in review queue
        existing_review = db.query(Review).filter(
            and_(
                Review.case_id == assessment.id,
                Review.case_type == "assessment"
            )
        ).first()
        
        if not existing_review:
            # Determine priority based on risk level and confidence
            if assessment.level == "High" and assessment.confidence < 50:
                priority = "high"
            elif assessment.level == "High" or assessment.confidence < 40:
                priority = "medium"
            else:
                priority = "low"
            
            # Create review record
            create_review(
                db=db,
                case_id=assessment.id,
                case_type="assessment",
                reviewer_id="system",  # System-generated review
                ai_decision={
                    "level": assessment.level,
                    "score": assessment.score,
                    "reasons": assessment.reasons,
                    "confidence": assessment.confidence
                },
                decision="needs_review",
                ai_confidence=assessment.confidence,
                priority=priority
            )
            queued_count += 1
    
    return queued_count

def queue_suspicious_pdf_checks(db: Session, authenticity_threshold: int = 30) -> int:
    """Queue PDF checks with low authenticity scores for human review"""
    
    # Find PDF checks with low authenticity scores that haven't been reviewed
    suspicious_pdfs = db.query(PDFCheck).filter(
        and_(
            PDFCheck.score < authenticity_threshold,
            PDFCheck.score.isnot(None)
        )
    ).all()
    
    queued_count = 0
    
    for pdf_check in suspicious_pdfs:
        # Check if already in review queue
        existing_review = db.query(Review).filter(
            and_(
                Review.case_id == pdf_check.id,
                Review.case_type == "pdf_check"
            )
        ).first()
        
        if not existing_review:
            # Determine priority based on authenticity score
            if pdf_check.score < 10:
                priority = "high"
            elif pdf_check.score < 20:
                priority = "medium"
            else:
                priority = "low"
            
            # Create review record
            create_review(
                db=db,
                case_id=pdf_check.id,
                case_type="pdf_check",
                reviewer_id="system",
                ai_decision={
                    "authenticity_score": pdf_check.score,
                    "is_likely_fake": pdf_check.is_likely_fake,
                    "anomalies": pdf_check.anomalies
                },
                decision="needs_review",
                ai_confidence=100 - pdf_check.score,  # Lower authenticity = higher need for review
                priority=priority
            )
            queued_count += 1
    
    return queued_count

def get_review_statistics(db: Session) -> dict:
    """Get review system statistics"""
    
    total_reviews = db.query(Review).count()
    pending_reviews = db.query(Review).filter(Review.status == "pending").count()
    completed_reviews = db.query(Review).filter(Review.status == "completed").count()
    
    # Count by priority
    high_priority = db.query(Review).filter(
        and_(Review.priority == "high", Review.status == "pending")
    ).count()
    medium_priority = db.query(Review).filter(
        and_(Review.priority == "medium", Review.status == "pending")
    ).count()
    low_priority = db.query(Review).filter(
        and_(Review.priority == "low", Review.status == "pending")
    ).count()
    
    # Count by case type
    assessment_reviews = db.query(Review).filter(Review.case_type == "assessment").count()
    pdf_reviews = db.query(Review).filter(Review.case_type == "pdf_check").count()
    
    # AI vs Human decision comparison (for completed reviews)
    completed_review_records = db.query(Review).filter(
        and_(
            Review.status == "completed",
            Review.decision.in_(["approve", "override"])
        )
    ).all()
    
    approvals = len([r for r in completed_review_records if r.decision == "approve"])
    overrides = len([r for r in completed_review_records if r.decision == "override"])
    
    return {
        "total_reviews": total_reviews,
        "pending_reviews": pending_reviews,
        "completed_reviews": completed_reviews,
        "pending_by_priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        },
        "reviews_by_type": {
            "assessments": assessment_reviews,
            "pdf_checks": pdf_reviews
        },
        "ai_vs_human": {
            "ai_approved": approvals,
            "human_overridden": overrides,
            "override_rate": round((overrides / (approvals + overrides)) * 100, 2) if (approvals + overrides) > 0 else 0
        }
    }