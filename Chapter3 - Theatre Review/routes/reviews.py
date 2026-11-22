from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import SQLModel, Session, select, func
from models import Review, CreateReview, ReadReview, UpdateReview
from database import get_session

router = APIRouter(prefix="/reviews", tags=["reviews"])

# Create a Review

@router.post("/", response_model=ReadReview)
def create_review(review: CreateReview, session: Session = Depends(get_session)):
    db_review = Review(**review.model_dump())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review

# Read all reviews or filter out some

@router.get("/", response_model=list[ReadReview])
def list_reviews(
    play_name: str | None = Query(None, description="Filter by play name"),
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=50, description="Max reviews to return"),
    session: Session = Depends(get_session)
):
    query = select(Review)
    if play_name:
        query = query.where(Review.play_name == play_name)

    query = query.offset(skip).limit(limit)
    query = query.order_by(Review.created_at.desc(), Review.id.desc())   
    reviews = session.exec(query).all()

    return reviews 

# Read a review with review_id

@router.get("/{review_id}", response_model=ReadReview)
def get_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail=f"No review found for the review_id: {review_id}")

    return review

# Update a review with review_id using PATCH

@router.patch("/{review_id}")
def update_review(review_id: int, update: UpdateReview, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail=f"No review found for the review_id: {review_id}")

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review, key, value)

    session.add(review)
    session.commit()
    session.refresh(review)

    return review

# Delete a review with review_id

@router.delete("/{review_id}")
def delete_review(review_id: int, session: Session = Depends(get_session)):
    review = session.get(Review, review_id)

    if not review:
        raise HTTPException(status_code=404, detail=f"No review found for the review_id: {review_id}")

    session.delete(review)
    session.commit()

    return {"message": f"Review with review_id: {review_id} got deleted"}

# Read the average of the reviews with play_name - Utilizing the func

@router.get("/average/{play_name}")
def get_average_rating(play_name: str, session: Session = Depends(get_session)):
    result = session.exec(
        select(func.avg(Review.rating), func.count(Review.id)).where(
            func.lower(Review.play_name) == play_name.lower()
            )
    ).first()

    avg_rating, total_reviews = result

    if total_reviews == 0:
        raise HTTPException(status_code=404, detail=f"No reviews found for {play_name}")
    
    return {
        "play_name": play_name,
        "average_rating": round(avg_rating,2),
        "total_reviews": total_reviews
    }