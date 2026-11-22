from fastapi import APIRouter, Depends, HTTPException, Query
from database import get_session
from models import Order, OrderStatus, OrderCreate, OrderUpdate, StatusLog
from sqlmodel import Session, select
from datetime import datetime, date, timezone

router = APIRouter(prefix="/orders", tags=["orders"])

# Create Orders
@router.post("/")
def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    db_order = Order(**order.model_dump())
    session.add(db_order)
    session.commit()
    session.refresh(db_order)

    return db_order

# Get all Orders and some optional queries as well
@router.get("/", response_model=list[Order])
def list_orders(
    status: OrderStatus | None = Query(default=None, description="Filter by order status"),
    created_date: date | None = Query(default=None, description="Filter by creation date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = select(Order)

    if status:
        query = query.where(Order.status == status)

    if created_date:
        start = datetime.combine(created_date, datetime.min.time(), tzinfo=timezone.utc)
        end = datetime.combine(created_date, datetime.max.time(), tzinfo=timezone.utc)
        query = query.where(Order.created_at >= start, Order.created_at <= end)

    query = query.offset(skip).limit(limit)
    orders = session.exec(query).all()

    if not orders:
        raise HTTPException(status_code=404,detail="No Orders found")
    
    return orders

# Get Particular order with order_id
@router.get("/{order_id}")
def get_order(
    order_id: int, session: Session = Depends(get_session)
):
    order = session.get(Order, order_id)

    if not order:
        raise HTTPException(status_code=404, detail=f"Order not found for the order_id: {order_id}")
    
    return order

# Update the order with order_id
@router.patch("/{order_id}")
def update_order(
    order_id:int,
    update:OrderUpdate,
    session:Session=Depends(get_session)
):
    
    order = session.get(Order, order_id)
    
    if not order:
        raise HTTPException(status_code=404,detail=f"Order not found for the order_id: {order_id}")
    
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)
 
    session.add(order)
    session.commit()
    session.refresh(order)
    
    return order

# Delete the order with order_id
@router.delete("/{order_id}")
def delete_order(
    order_id:int,
    session:Session=Depends(get_session)
):
    
    order_db = session.get(Order,order_id)
    if not order_db:
        raise HTTPException(status_code=404,detail=f"Order not found for the order_id: {order_id}")
    
    session.delete(order_db)
    session.commit()
    
    return {"message": f"Order with order_id: {order_id} got deleted"}