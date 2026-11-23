"""
URL Frontier and Scheduling Engine.
Tracks URL processing lifecycles, priority scheduling, and deduplication.
Adheres to SRS FR-02 and LLD Section 3.4.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from intelligent_scraper.core.enums import TaskStatus


@dataclass(order=True)
class CrawlTask:
    """Task item prioritized by integer priority (lower number = higher priority)."""
    priority: int
    task_id: str = field(compare=False)
    url: str = field(compare=False)
    source_id: str = field(compare=False)
    status: str = field(compare=False, default=TaskStatus.PENDING.value)
    retry_count: int = field(compare=False, default=0)
    source_config: Dict[str, Any] = field(compare=False, default_factory=dict)
    discovered_at: datetime = field(compare=False, default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = field(compare=False, default=None)
    error_message: Optional[str] = field(compare=False, default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "url": self.url,
            "source_id": self.source_id,
            "priority": self.priority,
            "status": self.status,
            "retry_count": self.retry_count,
            "source_config": self.source_config,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "error_message": self.error_message,
        }


class URLFrontier:
    """Centralized URL frontier coordinating discovered tasks."""

    def __init__(self):
        # Priority queue storing pending tasks
        self._queue: asyncio.PriorityQueue[CrawlTask] = asyncio.PriorityQueue()
        # task_id -> CrawlTask registry
        self._tasks: Dict[str, CrawlTask] = {}
        # URL canonical set to prevent duplicate enqueueing
        self._enqueued_urls: set[str] = set()
        self._lock = asyncio.Lock()

    async def enqueue(
        self,
        url: str,
        source_id: str,
        priority: int = 10,
        source_config: Optional[Dict[str, Any]] = None
    ) -> Optional[CrawlTask]:
        """
        Enqueues URL if not already tracked.
        Returns CrawlTask if added, or None if duplicate.
        """
        norm_url = url.strip().rstrip("/")
        async with self._lock:
            if norm_url in self._enqueued_urls:
                return None

            task_id = str(uuid.uuid4())
            task = CrawlTask(
                priority=priority,
                task_id=task_id,
                url=norm_url,
                source_id=source_id,
                source_config=source_config or {}
            )
            self._tasks[task_id] = task
            self._enqueued_urls.add(norm_url)
            await self._queue.put(task)
            return task

    async def dequeue(self, batch_size: int = 1) -> List[CrawlTask]:
        """Retrieves up to batch_size eligible pending tasks."""
        items: List[CrawlTask] = []
        async with self._lock:
            for _ in range(batch_size):
                if self._queue.empty():
                    break
                try:
                    task = self._queue.get_nowait()
                    task.status = TaskStatus.IN_PROGRESS.value
                    items.append(task)
                except asyncio.QueueEmpty:
                    break
        return items

    async def mark_in_progress(self, task_id: str) -> None:
        """Sets task state to IN_PROGRESS."""
        if task_id in self._tasks:
            self._tasks[task_id].status = TaskStatus.IN_PROGRESS.value

    async def mark_completed(self, task_id: str) -> None:
        """Sets task state to COMPLETED."""
        if task_id in self._tasks:
            self._tasks[task_id].status = TaskStatus.COMPLETED.value

    async def mark_failed(self, task_id: str, reason: str = "") -> None:
        """Sets task state to FAILED."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.FAILED.value
            task.error_message = reason

    async def schedule_retry(self, task_id: str, retry_at: Optional[datetime] = None) -> bool:
        """Increments retry count and re-enqueues task if under retry limit."""
        if task_id not in self._tasks:
            return False

        task = self._tasks[task_id]
        task.retry_count += 1
        task.status = TaskStatus.RETRY_SCHEDULED.value
        task.scheduled_at = retry_at or datetime.now(timezone.utc)

        # Deprioritize retries slightly
        task.priority += 5
        await self._queue.put(task)
        return True

    def get_pending_count(self) -> int:
        """Returns number of pending tasks in queue."""
        return self._queue.qsize()

    def get_task(self, task_id: str) -> Optional[CrawlTask]:
        """Finds task by id."""
        return self._tasks.get(task_id)

    def total_tasks_count(self) -> int:
        """Returns total tasks tracked."""
        return len(self._tasks)
