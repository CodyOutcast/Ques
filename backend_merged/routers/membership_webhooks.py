"""
Membership Webhook Router
Handles webhook events from membership service
"""

import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

from services.membership_slot_integration import MembershipSlotIntegrationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks/membership", tags=["Webhooks - Membership"])

class MembershipChangeEvent(BaseModel):
    """Schema for membership change webhook events"""
    user_id: int
    event_type: str  # "upgrade", "downgrade", "purchase", "cancel", "expire"
    old_membership: str
    new_membership: str
    subscription_end_date: str = None
    duration_months: int = None

class MembershipPurchaseEvent(BaseModel):
    """Schema for membership purchase webhook events"""
    user_id: int
    membership_type: str
    duration_months: int
    purchase_date: str

class MembershipCancelEvent(BaseModel):
    """Schema for membership cancellation webhook events"""
    user_id: int
    membership_type: str
    cancellation_date: str
    subscription_end_date: str

@router.post("/change")
async def handle_membership_change(
    event: MembershipChangeEvent,
    request: Request
):
    """
    Handle membership change webhook
    
    This endpoint is called when a user's membership changes
    """
    try:
        logger.info(f"Received membership change webhook: {event.dict()}")
        
        integration_service = MembershipSlotIntegrationService()
        
        # Parse subscription end date if provided
        subscription_end = None
        if event.subscription_end_date:
            subscription_end = datetime.fromisoformat(event.subscription_end_date.replace('Z', '+00:00'))
        
        # Handle different event types
        if event.event_type == "upgrade":
            success = integration_service.handle_membership_upgrade(
                user_id=event.user_id,
                old_membership=event.old_membership,
                new_membership=event.new_membership,
                subscription_end_date=subscription_end
            )
        elif event.event_type == "downgrade":
            success = integration_service.handle_membership_downgrade(
                user_id=event.user_id,
                old_membership=event.old_membership,
                new_membership=event.new_membership
            )
        elif event.event_type == "expire":
            success = integration_service.handle_membership_expiration(
                user_id=event.user_id
            )
        else:
            logger.warning(f"Unknown membership event type: {event.event_type}")
            success = False
        
        if success:
            logger.info(f"Successfully processed membership change for user {event.user_id}")
            return {
                "status": "success",
                "message": "Membership change processed",
                "user_id": event.user_id,
                "event_type": event.event_type
            }
        else:
            logger.error(f"Failed to process membership change for user {event.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process membership change"
            )
        
    except Exception as e:
        logger.error(f"Error processing membership change webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/purchase")
async def handle_membership_purchase(
    event: MembershipPurchaseEvent,
    request: Request
):
    """
    Handle membership purchase webhook
    
    This endpoint is called when a user purchases a membership
    """
    try:
        logger.info(f"Received membership purchase webhook: {event.dict()}")
        
        integration_service = MembershipSlotIntegrationService()
        
        # Handle subscription purchase
        success = integration_service.handle_subscription_purchase(
            user_id=event.user_id,
            membership_type=event.membership_type,
            duration_months=event.duration_months
        )
        
        if success:
            logger.info(f"Successfully processed membership purchase for user {event.user_id}")
            return {
                "status": "success",
                "message": "Membership purchase processed",
                "user_id": event.user_id,
                "membership_type": event.membership_type,
                "duration_months": event.duration_months
            }
        else:
            logger.error(f"Failed to process membership purchase for user {event.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process membership purchase"
            )
        
    except Exception as e:
        logger.error(f"Error processing membership purchase webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/cancel")
async def handle_membership_cancellation(
    event: MembershipCancelEvent,
    request: Request
):
    """
    Handle membership cancellation webhook
    
    This endpoint is called when a user cancels their membership
    """
    try:
        logger.info(f"Received membership cancellation webhook: {event.dict()}")
        
        integration_service = MembershipSlotIntegrationService()
        
        # Handle subscription cancellation
        success = integration_service.handle_subscription_cancellation(
            user_id=event.user_id
        )
        
        if success:
            logger.info(f"Successfully processed membership cancellation for user {event.user_id}")
            return {
                "status": "success",
                "message": "Membership cancellation processed",
                "user_id": event.user_id
            }
        else:
            logger.error(f"Failed to process membership cancellation for user {event.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process membership cancellation"
            )
        
    except Exception as e:
        logger.error(f"Error processing membership cancellation webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.get("/health")
async def webhook_health_check():
    """
    Health check endpoint for webhook service
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "membership-webhook"
    }
