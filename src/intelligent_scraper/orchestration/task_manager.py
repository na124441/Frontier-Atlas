"""
Task Manager.
Coordinates workflow stages, dispatches tasks, and tracks progress.
Adheres to LLD Section 10.2.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from intelligent_scraper.discovery.url_frontier import URLFrontier, CrawlTask
from intelligent_scraper.core.enums import TaskStatus

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages active task queues, dispatches batches, and tracks completion."""

    def __init__(self, frontier: Optional[URLFrontier] = None):
        self.frontier = frontier or URLFrontier()
        self.active_tasks: Dict[str, CrawlTask] = {}
        self.completed_count = 0
        self.failed_count = 0

    async def create_processing_tasks(self, discovered_urls: List[Dict[str, Any]]) -> List[CrawlTask]:
        """Registers discovered URLs into the frontier."""
        created = []
        for item in discovered_urls:
            url = item.get("url")
            source_name = item.get("source_name", "default")
            priority = item.get("priority", 10)
            task = await self.frontier.enqueue(url=url, source_id=source_name, priority=priority)
            if task:
                created.append(task)
        logger.info(f"Created {len(created)} new processing tasks in URL frontier.")
        return created

    async def dispatch_tasks_to_workers(self, batch_size: int = 10) -> List[CrawlTask]:
        """Fetches next pending batch of tasks."""
        batch = await self.frontier.dequeue(batch_size=batch_size)
        for task in batch:
            self.active_tasks[task.task_id] = task
        return batch

    async def mark_task_done(self, task_id: str, success: bool, reason: str = "") -> None:
        """Updates internal accounting on task completion or failure."""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]

        if success:
            self.completed_count += 1
            await self.frontier.mark_completed(task_id)
        else:
            self.failed_count += 1
            await self.frontier.mark_failed(task_id, reason)

    def get_stats(self) -> Dict[str, Any]:
        """Provides snapshot of crawler progress."""
        return {
            "pending": self.frontier.get_pending_count(),
            "active": len(self.active_tasks),
            "completed": self.completed_count,
            "failed": self.failed_count,
            "total_seen": self.frontier.total_tasks_count()
        }
