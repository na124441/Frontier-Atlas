"""Unit tests for URL Frontier."""
import pytest
from intelligent_scraper.discovery.url_frontier import URLFrontier
from intelligent_scraper.core.enums import TaskStatus


@pytest.mark.asyncio
async def test_url_frontier_enqueue_and_deduplicate():
    frontier = URLFrontier()

    task1 = await frontier.enqueue("https://example.com/ai", "test_source", priority=5)
    assert task1 is not None
    assert task1.url == "https://example.com/ai"
    assert task1.status == TaskStatus.PENDING.value

    # Duplicate enqueueing should return None
    task2 = await frontier.enqueue("https://example.com/ai", "test_source")
    assert task2 is None
    assert frontier.get_pending_count() == 1


@pytest.mark.asyncio
async def test_url_frontier_dequeue_and_status():
    frontier = URLFrontier()
    await frontier.enqueue("https://example.com/page1", "source1", priority=10)
    await frontier.enqueue("https://example.com/page2", "source1", priority=2)  # Higher priority

    batch = await frontier.dequeue(batch_size=2)
    assert len(batch) == 2
    # Lowest integer priority should dequeue first
    assert batch[0].priority == 2
    assert batch[0].status == TaskStatus.IN_PROGRESS.value

    await frontier.mark_completed(batch[0].task_id)
    assert frontier.get_task(batch[0].task_id).status == TaskStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_url_frontier_retry_scheduling():
    frontier = URLFrontier()
    task = await frontier.enqueue("https://example.com/retry", "source1")
    assert task is not None

    dequeued = await frontier.dequeue(batch_size=1)
    await frontier.schedule_retry(dequeued[0].task_id)

    updated_task = frontier.get_task(dequeued[0].task_id)
    assert updated_task.retry_count == 1
    assert updated_task.status == TaskStatus.RETRY_SCHEDULED.value
    assert frontier.get_pending_count() == 1
