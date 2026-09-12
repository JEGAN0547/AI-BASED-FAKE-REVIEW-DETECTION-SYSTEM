"""
AI-Based Fake Review Detection System
FastAPI REST API Server (Master Project Edition)
"""

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import datetime
import re

from backend.database import (
    init_db, save_review, get_all_reviews,
    get_review_by_id, delete_review_by_id, get_dashboard_stats
)

app = FastAPI(
    title="AI-Based Fake Review Detection API",
    description="REST API for analyzing review authenticity, calculating confidence scores, and providing Explainable AI insights.",
    version="2.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Schema on Startup
init_db()


# Input & Output Schemas
class AnalyzeReviewRequest(BaseModel):
    product_name: Optional[str] = Field(default="General Product", example="AuraSound Pro Headphones")
    review_text: str = Field(..., example="AMAZING PRODUCT BEST HEADPHONES IN THE WORLD!!! BUY NOW FAST!")
    rating: int = Field(default=5, ge=1, le=5)
    reviewer_name: Optional[str] = Field(default="Anonymous User", example="John Doe")
    review_date: Optional[str] = Field(default=None, example="2026-09-12")

class ExplainableFactors(BaseModel):
    excessive_positive: int
    repeated_phrases: int
    mismatch: int
    length: int
    promotional: int

class ReviewResponse(BaseModel):
    id: str
    product_name: str
    review_text: str
    rating: int
    reviewer_name: str
    review_date: str
    prediction: str
    confidence_score: int
    sentiment: str
    suspicious_factors: str
    explainable_factors: ExplainableFactors
    recommendation: str
    created_at: str


# NLP Classification Core Engine
def perform_ai_analysis(product_name: str, text: str, rating: int, reviewer: str, date_str: str) -> dict:
    clean_text = text.strip()
    words = clean_text.split()
    word_count = len(words)

    if word_count == 0:
        raise ValueError("Review text cannot be empty.")

    # 1. Text Metrics
    uppercase_chars = len(re.findall(r'[A-Z]', clean_text))
    total_letters = len(re.findall(r'[a-zA-Z]', clean_text)) or 1
    uppercase_ratio = uppercase_chars / total_letters

    exclamation_count = len(re.findall(r'!', clean_text))

    # 2. Pattern Matching
    spam_triggers = [
        "buy now", "fast shipping", "must buy", "aaa+++", "best seller",
        "click here", "100% perfect", "100% working", "money back guarantee",
        "great product great seller", "item received in good condition",
        "satisfied with seller", "highly recommend this store", "best product ever",
        "amazing amazing", "go buy", "instead of this", "scam product"
    ]

    lower_text = clean_text.lower()
    triggered = []

    promotional_score = 0
    for phrase in spam_triggers:
        if phrase in lower_text:
            triggered.append(f'Spam phrase: "{phrase}"')
            promotional_score += 25

    promotional_score = min(promotional_score, 100)

    # 3. Sentiment & Polarity Analysis
    pos_words = ["amazing", "excellent", "great", "awesome", "fantastic", "perfect", "love", "best", "superb"]
    neg_words = ["terrible", "garbage", "horrible", "awful", "scam", "useless", "broken", "worst", "junk"]

    pos_count = sum(1 for w in words if w.lower().strip("!.,?") in pos_words)
    neg_count = sum(1 for w in words if w.lower().strip("!.,?") in neg_words)

    excessive_pos_score = min(int((pos_count / max(word_count, 1)) * 250), 100)

    # 4. Repeated Words / Phrases
    unique_words = set(w.lower() for w in words)
    repetition_score = min(int((1 - (len(unique_words) / max(word_count, 1))) * 180), 100)

    # 5. Rating Mismatch Score
    mismatch_score = 0
    if rating >= 4 and neg_count > pos_count + 1:
        mismatch_score = 85
        triggered.append("High rating with negative sentiment mismatch")
    elif rating <= 2 and pos_count > neg_count + 1:
        mismatch_score = 85
        triggered.append("Low rating with positive sentiment mismatch")

    # 6. Length Score
    length_score = 90 if word_count < 8 else (45 if word_count < 15 else 10)
    if word_count < 8:
        triggered.append("Unusually short review length")

    if uppercase_ratio > 0.35:
        triggered.append(f"Excessive UPPERCASE ({int(uppercase_ratio * 100)}%)")
    if exclamation_count >= 3:
        triggered.append(f"Excessive exclamation marks ({exclamation_count})")

    # 7. Composite Fake Score Calculation (0 to 100)
    composite_fake_score = int(
        (promotional_score * 0.30) +
        (excessive_pos_score * 0.25) +
        (mismatch_score * 0.20) +
        (repetition_score * 0.15) +
        (length_score * 0.10)
    )

    # Determine Prediction Category & Confidence
    if composite_fake_score >= 65:
        prediction = "Fake Review"
        confidence_score = min(75 + int(composite_fake_score * 0.22), 98)
        recommendation = "High risk of deceptive or automated spam review. Flag or suppress from product rating."
    elif composite_fake_score >= 40:
        prediction = "Suspicious Review"
        confidence_score = 70 + int((composite_fake_score - 40) * 0.3)
        recommendation = "Contains repetitive or template characteristics. Recommend manual verification."
    else:
        prediction = "Genuine Review"
        confidence_score = min(82 + int((100 - composite_fake_score) * 0.16), 97)
        recommendation = "Appears organically written and trustworthy. No action needed."

    # Sentiment Label
    if pos_count > neg_count + 2:
        sentiment = "Extremely Positive"
    elif pos_count > neg_count:
        sentiment = "Positive"
    elif neg_count > pos_count:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    factors_str = ", ".join(triggered) if triggered else "Natural vocabulary flow, consistent rating sentiment"

    return {
        "product_name": product_name or "General Product",
        "review_text": clean_text,
        "rating": rating,
        "reviewer_name": reviewer or "Anonymous User",
        "review_date": date_str or datetime.date.today().strftime("%Y-%m-%d"),
        "prediction": prediction,
        "confidence_score": confidence_score,
        "sentiment": sentiment,
        "suspicious_factors": factors_str,
        "explainable_factors": {
            "excessive_positive": excessive_pos_score,
            "repeated_phrases": repetition_score,
            "mismatch": mismatch_score,
            "length": length_score,
            "promotional": promotional_score
        },
        "recommendation": recommendation
    }


# REST API Endpoints matching Master Prompt specifications

@app.get("/api/health")
def health_check():
    return {"status": "online", "service": "AI-Based Fake Review Detection API", "version": "2.0.0"}

@app.post("/api/analyze-review", response_model=ReviewResponse)
def analyze_review(req: AnalyzeReviewRequest):
    """Analyze a new review using AI/ML rules, store in DB, and return result."""
    try:
        analysis = perform_ai_analysis(
            req.product_name, req.review_text, req.rating,
            req.reviewer_name, req.review_date
        )
        saved_record = save_review(analysis)
        return saved_record
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"AI model analysis error: {str(err)}")

@app.get("/api/reviews")
def list_reviews():
    """Retrieve all previously analyzed reviews from database."""
    reviews = get_all_reviews()
    return {"count": len(reviews), "reviews": reviews}

@app.get("/api/reviews/{review_id}")
def get_single_review(review_id: str = Path(..., title="Review ID")):
    """Get single review analysis by ID."""
    review = get_review_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Review with ID '{review_id}' not found.")
    return review

@app.delete("/api/reviews/{review_id}")
def remove_review(review_id: str = Path(..., title="Review ID")):
    """Delete a review from history database."""
    success = delete_review_by_id(review_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Review with ID '{review_id}' not found or already deleted.")
    return {"success": True, "message": f"Review '{review_id}' deleted successfully."}

@app.get("/api/dashboard")
def get_dashboard_data():
    """Get aggregate admin analytics and statistics for dashboard charts."""
    return get_dashboard_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
