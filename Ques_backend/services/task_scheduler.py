"""
Task Scheduler Service
Handles background tasks and scheduling
"""

import asyncio
import logging
import time
from typing import List, Callable, Optional
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class TaskScheduler:
    """Simple task scheduler for background operations"""
    
    def __init__(self):
        self.tasks: List[asyncio.Task] = []
        self.running = False
    
    def add_task(self, coro: Callable, name: str = "background_task"):
        """Add a background task"""
        if self.running:
            task = asyncio.create_task(coro(), name=name)
            self.tasks.append(task)
            logger.info(f"Added background task: {name}")
    
    async def start(self):
        """Start the task scheduler"""
        self.running = True
        logger.info("Task scheduler started")
    
    async def stop(self):
        """Stop the task scheduler and cancel all tasks"""
        self.running = False
        
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to be cancelled
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("Task scheduler stopped")


# Global task scheduler instance
_scheduler = TaskScheduler()


async def cleanup_expired_casual_requests_task():
    """
    Background task to cleanup expired casual requests
    As specified in casual_request_integration_guide_en.md
    """
    while True:
        try:
            # Wait 24 hours between cleanup runs (execute at 3:00 AM daily equivalent)
            await asyncio.sleep(24 * 60 * 60)
            
            # Import here to avoid circular imports
            from dependencies.db import get_db
            from models.casual_requests import CasualRequest
            from services.casual_vector_setup import clean_expired_casual_request_vectors
            import os
            
            # Cleanup database records
            db = next(get_db())
            try:
                deleted_count = CasualRequest.cleanup_expired(db, days_threshold=7)
                logger.info(f"Cleaned up {deleted_count} expired casual requests from database")
            finally:
                db.close()
            
            # Cleanup vector database records if configured
            try:
                # Only attempt vector cleanup if Qdrant is configured
                qdrant_url = os.getenv("QDRANT_URL")
                if qdrant_url:
                    from qdrant_client import QdrantClient
                    qdrant_client = QdrantClient(url=qdrant_url)
                    vector_deleted = clean_expired_casual_request_vectors(
                        qdrant_client, 
                        collection_name="casual_requests",
                        days_threshold=7
                    )
                    logger.info(f"Cleaned up {vector_deleted} expired casual requests from vector database")
            except Exception as e:
                logger.warning(f"Vector database cleanup failed: {e}")
                
        except Exception as e:
            logger.error(f"Casual requests cleanup task failed: {e}")
            # Wait 1 hour before retrying on error
            await asyncio.sleep(60 * 60)


async def start_background_tasks():
    """Start background tasks"""
    await _scheduler.start()
    
    # Add your background tasks here
    # Example: _scheduler.add_task(cleanup_expired_sessions, "session_cleanup")
    
    # Add casual requests cleanup task as specified in integration guide
    _scheduler.add_task(cleanup_expired_casual_requests_task, "casual_requests_cleanup")
    
    logger.info("Background tasks started")


async def stop_background_tasks():
    """Stop background tasks"""
    await _scheduler.stop()
    logger.info("Background tasks stopped")


def get_scheduler() -> TaskScheduler:
    """Get the global task scheduler instance"""
    return _scheduler