"""
Task Scheduler Service
Handles background tasks and scheduling
"""

import asyncio
import logging
from typing import List, Callable, Optional


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


async def start_background_tasks():
    """Start background tasks"""
    await _scheduler.start()
    
    # Add your background tasks here
    # Example: _scheduler.add_task(cleanup_expired_sessions, "session_cleanup")
    
    logger.info("Background tasks started")


async def stop_background_tasks():
    """Stop background tasks"""
    await _scheduler.stop()
    logger.info("Background tasks stopped")


def get_scheduler() -> TaskScheduler:
    """Get the global task scheduler instance"""
    return _scheduler