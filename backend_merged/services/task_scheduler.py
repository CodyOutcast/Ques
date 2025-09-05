"""
Task Scheduler Service
Handles background tasks like membership expiration checks
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from services.membership_slot_integration import MembershipSlotIntegrationService

logger = logging.getLogger(__name__)

class TaskSchedulerService:
    """
    Service for running scheduled background tasks
    """
    
    def __init__(self):
        self.membership_integration = MembershipSlotIntegrationService()
        self.is_running = False
        self.tasks = {}
    
    async def start_scheduler(self):
        """
        Start the task scheduler
        """
        logger.info("Starting task scheduler")
        self.is_running = True
        
        # Schedule daily membership check
        asyncio.create_task(self._schedule_daily_membership_check())
        
        logger.info("Task scheduler started")
    
    async def stop_scheduler(self):
        """
        Stop the task scheduler
        """
        logger.info("Stopping task scheduler")
        self.is_running = False
        
        # Cancel all running tasks
        for task_name, task in self.tasks.items():
            if task and not task.done():
                logger.info(f"Cancelling task: {task_name}")
                task.cancel()
        
        logger.info("Task scheduler stopped")
    
    async def _schedule_daily_membership_check(self):
        """
        Schedule daily membership expiration checks
        """
        while self.is_running:
            try:
                # Calculate time until next midnight
                now = datetime.now()
                tomorrow = now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
                sleep_seconds = (tomorrow - now).total_seconds()
                
                logger.info(f"Next membership check scheduled in {sleep_seconds/3600:.1f} hours")
                
                # Wait until 2 AM next day
                await asyncio.sleep(sleep_seconds)
                
                if self.is_running:
                    logger.info("Running scheduled membership check")
                    await self._run_daily_membership_check()
                
            except asyncio.CancelledError:
                logger.info("Daily membership check task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in daily membership check scheduler: {str(e)}")
                # Wait 1 hour before trying again
                await asyncio.sleep(3600)
    
    async def _run_daily_membership_check(self):
        """
        Run the daily membership expiration check
        """
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                self.membership_integration.run_daily_membership_check
            )
            
            logger.info(f"Daily membership check completed: {results}")
            
        except Exception as e:
            logger.error(f"Error running daily membership check: {str(e)}")
    
    async def run_membership_check_now(self) -> Dict[str, Any]:
        """
        Run membership check immediately (for testing/admin purposes)
        
        Returns:
            Results of the membership check
        """
        logger.info("Running immediate membership check")
        
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self.membership_integration.run_daily_membership_check
            )
            
            logger.info(f"Immediate membership check completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in immediate membership check: {str(e)}")
            return {
                "expired_memberships": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e)
            }

# Global task scheduler instance
task_scheduler = TaskSchedulerService()

async def start_background_tasks():
    """
    Start all background tasks
    """
    await task_scheduler.start_scheduler()

async def stop_background_tasks():
    """
    Stop all background tasks
    """
    await task_scheduler.stop_scheduler()

def get_task_scheduler() -> TaskSchedulerService:
    """
    Get the global task scheduler instance
    """
    return task_scheduler
