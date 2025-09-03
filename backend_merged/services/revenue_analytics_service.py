"""
Revenue Analytics Service
Provides comprehensive revenue tracking and analytics over time
"""

from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, extract, case
from decimal import Decimal
import logging
from collections import defaultdict

from models.payments import MembershipTransaction, PaymentStatus, PaymentMethod
from models.user_membership import UserMembership, MembershipType
from models.users import User

logger = logging.getLogger(__name__)

class RevenueAnalyticsService:
    """Service for revenue analytics and tracking"""
    
    @staticmethod
    def get_revenue_overview(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get overall revenue overview for the specified period
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get successful transactions in the period
        transactions = db.query(MembershipTransaction).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                MembershipTransaction.paid_at >= start_date,
                MembershipTransaction.paid_at <= end_date
            )
        ).all()
        
        total_revenue = sum(t.amount for t in transactions)
        transaction_count = len(transactions)
        
        # Calculate daily averages
        avg_daily_revenue = total_revenue / days if days > 0 else 0
        avg_transaction_value = total_revenue / transaction_count if transaction_count > 0 else 0
        
        # Get previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_transactions = db.query(MembershipTransaction).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                MembershipTransaction.paid_at >= prev_start,
                MembershipTransaction.paid_at < start_date
            )
        ).all()
        
        prev_revenue = sum(t.amount for t in prev_transactions)
        revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        
        return {
            "period_days": days,
            "total_revenue": float(total_revenue),
            "transaction_count": transaction_count,
            "avg_daily_revenue": float(avg_daily_revenue),
            "avg_transaction_value": float(avg_transaction_value),
            "revenue_growth_percent": float(revenue_growth),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    
    @staticmethod
    def get_daily_revenue_chart(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily revenue data for charting
        """
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query daily revenue
        daily_revenue = db.query(
            func.date(MembershipTransaction.paid_at).label('date'),
            func.sum(MembershipTransaction.amount).label('revenue'),
            func.count(MembershipTransaction.id).label('transactions')
        ).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                func.date(MembershipTransaction.paid_at) >= start_date,
                func.date(MembershipTransaction.paid_at) <= end_date
            )
        ).group_by(
            func.date(MembershipTransaction.paid_at)
        ).order_by(
            func.date(MembershipTransaction.paid_at)
        ).all()
        
        # Create a complete date range with zero-fill
        revenue_dict = {row.date: {"revenue": float(row.revenue), "transactions": row.transactions} 
                       for row in daily_revenue}
        
        chart_data = []
        current_date = start_date
        
        while current_date <= end_date:
            data = revenue_dict.get(current_date, {"revenue": 0.0, "transactions": 0})
            chart_data.append({
                "date": current_date.isoformat(),
                "revenue": data["revenue"],
                "transactions": data["transactions"]
            })
            current_date += timedelta(days=1)
        
        return chart_data
    
    @staticmethod
    def get_monthly_revenue_chart(db: Session, months: int = 12) -> List[Dict[str, Any]]:
        """
        Get monthly revenue data for charting
        """
        # Calculate start and end dates
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=months * 31)  # Approximate
        
        # Query monthly revenue
        monthly_revenue = db.query(
            extract('year', MembershipTransaction.paid_at).label('year'),
            extract('month', MembershipTransaction.paid_at).label('month'),
            func.sum(MembershipTransaction.amount).label('revenue'),
            func.count(MembershipTransaction.id).label('transactions')
        ).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                MembershipTransaction.paid_at >= start_date
            )
        ).group_by(
            extract('year', MembershipTransaction.paid_at),
            extract('month', MembershipTransaction.paid_at)
        ).order_by(
            extract('year', MembershipTransaction.paid_at),
            extract('month', MembershipTransaction.paid_at)
        ).all()
        
        chart_data = []
        for row in monthly_revenue:
            chart_data.append({
                "year": int(row.year),
                "month": int(row.month),
                "month_name": datetime(int(row.year), int(row.month), 1).strftime("%B %Y"),
                "revenue": float(row.revenue),
                "transactions": row.transactions
            })
        
        return chart_data
    
    @staticmethod
    def get_revenue_by_membership_type(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get revenue breakdown by membership type
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query revenue by plan type
        revenue_by_type = db.query(
            MembershipTransaction.plan_type,
            func.sum(MembershipTransaction.amount).label('revenue'),
            func.count(MembershipTransaction.id).label('transactions'),
            func.avg(MembershipTransaction.amount).label('avg_amount')
        ).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                MembershipTransaction.paid_at >= start_date,
                MembershipTransaction.paid_at <= end_date
            )
        ).group_by(
            MembershipTransaction.plan_type
        ).order_by(
            desc(func.sum(MembershipTransaction.amount))
        ).all()
        
        breakdown = []
        total_revenue = sum(row.revenue for row in revenue_by_type)
        
        for row in revenue_by_type:
            percentage = (row.revenue / total_revenue * 100) if total_revenue > 0 else 0
            breakdown.append({
                "plan_type": row.plan_type,
                "revenue": float(row.revenue),
                "transactions": row.transactions,
                "avg_amount": float(row.avg_amount),
                "percentage": float(percentage)
            })
        
        return breakdown
    
    @staticmethod
    def get_revenue_by_payment_method(db: Session, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get revenue breakdown by payment method
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query revenue by payment method
        revenue_by_method = db.query(
            MembershipTransaction.payment_method,
            func.sum(MembershipTransaction.amount).label('revenue'),
            func.count(MembershipTransaction.id).label('transactions')
        ).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                MembershipTransaction.paid_at >= start_date,
                MembershipTransaction.paid_at <= end_date
            )
        ).group_by(
            MembershipTransaction.payment_method
        ).order_by(
            desc(func.sum(MembershipTransaction.amount))
        ).all()
        
        breakdown = []
        total_revenue = sum(row.revenue for row in revenue_by_method)
        
        for row in revenue_by_method:
            percentage = (row.revenue / total_revenue * 100) if total_revenue > 0 else 0
            breakdown.append({
                "payment_method": row.payment_method.value,
                "revenue": float(row.revenue),
                "transactions": row.transactions,
                "percentage": float(percentage)
            })
        
        return breakdown
    
    @staticmethod
    def get_user_revenue_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get user-related revenue analytics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get paying users
        paying_users = db.query(
            MembershipTransaction.user_id,
            func.sum(MembershipTransaction.amount).label('total_spent'),
            func.count(MembershipTransaction.id).label('transaction_count')
        ).filter(
            and_(
                MembershipTransaction.payment_status == PaymentStatus.SUCCESS,
                MembershipTransaction.paid_at >= start_date,
                MembershipTransaction.paid_at <= end_date
            )
        ).group_by(
            MembershipTransaction.user_id
        ).subquery()
        
        # Get statistics
        user_stats = db.query(
            func.count(paying_users.c.user_id).label('paying_users'),
            func.avg(paying_users.c.total_spent).label('avg_revenue_per_user'),
            func.max(paying_users.c.total_spent).label('max_revenue_per_user'),
            func.sum(paying_users.c.total_spent).label('total_revenue')
        ).first()
        
        # Get total users for conversion rate
        total_users = db.query(func.count(User.user_id)).scalar()
        conversion_rate = (user_stats.paying_users / total_users * 100) if total_users > 0 else 0
        
        return {
            "paying_users": user_stats.paying_users or 0,
            "total_users": total_users or 0,
            "conversion_rate_percent": float(conversion_rate),
            "avg_revenue_per_user": float(user_stats.avg_revenue_per_user or 0),
            "max_revenue_per_user": float(user_stats.max_revenue_per_user or 0),
            "total_revenue": float(user_stats.total_revenue or 0)
        }
    
    @staticmethod
    def get_recurring_revenue_metrics(db: Session) -> Dict[str, Any]:
        """
        Get recurring revenue metrics (MRR, ARR)
        """
        current_date = datetime.utcnow()
        
        # Get active memberships
        active_memberships = db.query(UserMembership).filter(
            and_(
                UserMembership.membership_type != MembershipType.FREE,
                or_(
                    UserMembership.end_date.is_(None),
                    UserMembership.end_date > current_date
                )
            )
        ).all()
        
        # Calculate monthly and annual recurring revenue
        mrr = 0.0  # Monthly Recurring Revenue
        arr = 0.0  # Annual Recurring Revenue
        
        for membership in active_memberships:
            # Get the latest successful transaction for this user
            latest_transaction = db.query(MembershipTransaction).filter(
                and_(
                    MembershipTransaction.user_id == membership.user_id,
                    MembershipTransaction.payment_status == PaymentStatus.SUCCESS
                )
            ).order_by(desc(MembershipTransaction.paid_at)).first()
            
            if latest_transaction:
                # Estimate monthly revenue based on plan duration
                if latest_transaction.plan_duration_days == 30:  # Monthly
                    mrr += latest_transaction.amount
                elif latest_transaction.plan_duration_days == 365:  # Annual
                    annual_amount = latest_transaction.amount
                    mrr += annual_amount / 12
                    arr += annual_amount
        
        # Calculate ARR from MRR if not already calculated
        if arr == 0:
            arr = mrr * 12
        
        return {
            "monthly_recurring_revenue": float(mrr),
            "annual_recurring_revenue": float(arr),
            "active_subscribers": len(active_memberships),
            "calculation_date": current_date.isoformat()
        }
    
    @staticmethod
    def get_churn_and_retention_metrics(db: Session) -> Dict[str, Any]:
        """
        Get customer churn and retention metrics
        """
        current_date = datetime.utcnow()
        last_month = current_date - timedelta(days=30)
        two_months_ago = current_date - timedelta(days=60)
        
        # Users who had active membership last month
        users_last_month = db.query(UserMembership.user_id).filter(
            and_(
                UserMembership.end_date >= last_month,
                UserMembership.end_date < current_date,
                UserMembership.membership_type != MembershipType.FREE
            )
        ).distinct().count()
        
        # Users who still have active membership
        retained_users = db.query(UserMembership.user_id).filter(
            and_(
                UserMembership.end_date >= current_date,
                UserMembership.membership_type != MembershipType.FREE,
                UserMembership.user_id.in_(
                    db.query(UserMembership.user_id).filter(
                        and_(
                            UserMembership.end_date >= last_month,
                            UserMembership.end_date < current_date
                        )
                    )
                )
            )
        ).distinct().count()
        
        # Calculate metrics
        retention_rate = (retained_users / users_last_month * 100) if users_last_month > 0 else 0
        churn_rate = 100 - retention_rate
        
        return {
            "users_last_month": users_last_month,
            "retained_users": retained_users,
            "retention_rate_percent": float(retention_rate),
            "churn_rate_percent": float(churn_rate),
            "calculation_period": "30_days"
        }
    
    @staticmethod
    def get_comprehensive_revenue_report(db: Session, days: int = 30) -> Dict[str, Any]:
        """
        Get a comprehensive revenue report combining all metrics
        """
        return {
            "overview": RevenueAnalyticsService.get_revenue_overview(db, days),
            "daily_chart": RevenueAnalyticsService.get_daily_revenue_chart(db, days),
            "monthly_chart": RevenueAnalyticsService.get_monthly_revenue_chart(db, 12),
            "membership_breakdown": RevenueAnalyticsService.get_revenue_by_membership_type(db, days),
            "payment_method_breakdown": RevenueAnalyticsService.get_revenue_by_payment_method(db, days),
            "user_analytics": RevenueAnalyticsService.get_user_revenue_analytics(db, days),
            "recurring_revenue": RevenueAnalyticsService.get_recurring_revenue_metrics(db),
            "churn_retention": RevenueAnalyticsService.get_churn_and_retention_metrics(db),
            "generated_at": datetime.utcnow().isoformat()
        }
