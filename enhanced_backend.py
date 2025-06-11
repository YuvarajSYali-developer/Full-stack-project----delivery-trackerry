#!/usr/bin/env python3
"""
Enhanced Shipment Management Backend - Part 2: Shipment Endpoints
"""

# This file contains the shipment management endpoints to be added to the main backend

# Shipment management endpoints
shipment_endpoints = '''

# Shipment CRUD endpoints
@app.post("/shipments/", response_model=ShipmentRead)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new shipment"""
    try:
        logger.info(f"Creating shipment for user: {current_user.username}")
        
        # Check if tracking number exists
        existing = db.exec(select(Shipment).where(Shipment.tracking_number == shipment.tracking_number)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tracking number already exists")
        
        # Create shipment
        db_shipment = Shipment(
            **shipment.model_dump(),
            created_by=current_user.id,
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(db_shipment)
        db.commit()
        db.refresh(db_shipment)
        
        # Create initial history entry
        history = ShipmentHistory(
            shipment_id=db_shipment.id,
            status=db_shipment.status,
            location=db_shipment.origin,
            notes=f"Shipment created by {current_user.username}",
            updated_by=current_user.id
        )
        db.add(history)
        db.commit()
        
        logger.info(f"Shipment created: {db_shipment.tracking_number}")
        return db_shipment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shipment creation error: {e}")
        raise HTTPException(status_code=500, detail="Error creating shipment")

@app.get("/shipments/", response_model=List[ShipmentRead])
def read_shipments(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    search: str = None,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get shipments with optional filtering"""
    query = select(Shipment)
    
    # Apply filters
    if status:
        query = query.where(Shipment.status == status)
    
    if search:
        query = query.where(
            (Shipment.tracking_number.contains(search)) |
            (Shipment.origin.contains(search)) |
            (Shipment.destination.contains(search)) |
            (Shipment.description.contains(search))
        )
    
    # Non-admin users can only see their own shipments
    if not current_user.is_admin:
        query = query.where(Shipment.created_by == current_user.id)
    
    shipments = db.exec(query.offset(skip).limit(limit)).all()
    return shipments

@app.get("/shipments/{shipment_id}", response_model=ShipmentRead)
def read_shipment(
    shipment_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific shipment"""
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Check permissions
    if not current_user.is_admin and shipment.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return shipment

@app.get("/shipments/track/{tracking_number}", response_model=ShipmentRead)
def track_shipment(
    tracking_number: str,
    db: Session = Depends(get_session)
):
    """Public endpoint to track shipment by tracking number"""
    shipment = db.exec(select(Shipment).where(Shipment.tracking_number == tracking_number)).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    return shipment

@app.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update a shipment"""
    try:
        db_shipment = db.get(Shipment, shipment_id)
        if not db_shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Check permissions
        if not current_user.is_admin and db_shipment.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        update_data = shipment_update.model_dump(exclude_unset=True)
        old_status = db_shipment.status
        
        for field, value in update_data.items():
            setattr(db_shipment, field, value)
        
        db_shipment.updated_at = datetime.now(timezone.utc)
        
        # If status changed, create history entry
        if "status" in update_data and update_data["status"] != old_status:
            history = ShipmentHistory(
                shipment_id=shipment_id,
                status=update_data["status"],
                notes=f"Status updated by {current_user.username}",
                updated_by=current_user.id
            )
            db.add(history)
        
        db.add(db_shipment)
        db.commit()
        db.refresh(db_shipment)
        
        logger.info(f"Shipment updated: {db_shipment.tracking_number}")
        return db_shipment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Shipment update error: {e}")
        raise HTTPException(status_code=500, detail="Error updating shipment")

@app.delete("/shipments/{shipment_id}")
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a shipment"""
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    # Check permissions
    if not current_user.is_admin and shipment.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete related history first
    history_records = db.exec(select(ShipmentHistory).where(ShipmentHistory.shipment_id == shipment_id)).all()
    for history in history_records:
        db.delete(history)
    
    db.delete(shipment)
    db.commit()
    
    logger.info(f"Shipment deleted: {shipment.tracking_number}")
    return {"message": "Shipment deleted successfully"}

# Shipment history endpoints
@app.get("/shipments/{shipment_id}/history", response_model=List[ShipmentHistoryRead])
def get_shipment_history(
    shipment_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get shipment history"""
    # Check if shipment exists and user has access
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    if not current_user.is_admin and shipment.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    history = db.exec(
        select(ShipmentHistory)
        .where(ShipmentHistory.shipment_id == shipment_id)
        .order_by(ShipmentHistory.timestamp.desc())
    ).all()
    
    return history

@app.post("/shipments/{shipment_id}/history", response_model=ShipmentHistoryRead)
def add_shipment_history(
    shipment_id: int,
    history: ShipmentHistoryCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Add a history entry to a shipment"""
    # Check if shipment exists and user has access
    shipment = db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    if not current_user.is_admin and shipment.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create history entry
    db_history = ShipmentHistory(
        shipment_id=shipment_id,
        **history.model_dump(),
        updated_by=current_user.id
    )
    
    # Update shipment status if provided
    if history.status and history.status != shipment.status:
        shipment.status = history.status
        shipment.updated_at = datetime.now(timezone.utc)
        db.add(shipment)
    
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return db_history

# Analytics endpoints
@app.get("/analytics/dashboard")
def get_dashboard_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """Get dashboard analytics"""
    # Base query
    base_query = select(Shipment)
    if not current_user.is_admin:
        base_query = base_query.where(Shipment.created_by == current_user.id)
    
    # Get counts by status
    status_counts = {}
    for status in ["pending", "shipped", "in_transit", "delivered", "cancelled"]:
        count = len(db.exec(base_query.where(Shipment.status == status)).all())
        status_counts[status] = count
    
    # Get total shipments
    total_shipments = len(db.exec(base_query).all())
    
    # Get recent shipments
    recent_shipments = db.exec(
        base_query.order_by(Shipment.created_at.desc()).limit(5)
    ).all()
    
    return {
        "total_shipments": total_shipments,
        "status_counts": status_counts,
        "recent_shipments": [
            {
                "id": s.id,
                "tracking_number": s.tracking_number,
                "status": s.status,
                "origin": s.origin,
                "destination": s.destination,
                "created_at": s.created_at
            } for s in recent_shipments
        ]
    }

'''

print("Shipment endpoints code generated. Add this to the main backend file.")
