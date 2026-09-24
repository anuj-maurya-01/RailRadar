"""Automatic Periodic Train Data Collection Scheduler.

Utilizes APScheduler (AsyncIOScheduler) to trigger non-overlapping periodic
live train data collection for configured tracked trains.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    from zoneinfo import ZoneInfo
    IST_TZ = ZoneInfo("Asia/Kolkata")
except Exception:
    IST_TZ = timezone(timedelta(hours=5, minutes=30), name="IST")

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import COLLECTION_INTERVAL_MINUTES, TRACKED_TRAIN_NUMBERS
from app.services.data_collector import get_data_collector, DataCollectorError
from app.services.railway_api import RailwayAPIException

logger = logging.getLogger(__name__)


class CollectionScheduler:
    """Manages the periodic collection lifecycle and in-memory status reporting."""

    def __init__(
        self,
        interval_minutes: int = COLLECTION_INTERVAL_MINUTES,
        tracked_trains: Optional[List[str]] = None,
    ):
        self.interval_minutes = interval_minutes
        self.tracked_trains = (
            tracked_trains if tracked_trains is not None else list(TRACKED_TRAIN_NUMBERS)
        )

        self.scheduler: Optional[AsyncIOScheduler] = None
        self._is_cycle_running = False
        self._lock = asyncio.Lock()

        # In-memory runtime tracking
        self.last_collection_started_at: Optional[str] = None
        self.last_collection_completed_at: Optional[str] = None
        self.last_success_count: int = 0
        self.last_failure_count: int = 0
        self.last_errors: List[Dict[str, Any]] = []
        self.total_cycles_run: int = 0

    @property
    def is_running(self) -> bool:
        """Check if the scheduler is actively running."""
        return self.scheduler is not None and self.scheduler.running

    def start(self) -> None:
        """Start the periodic collection scheduler on application startup."""
        if self.is_running:
            logger.warning("[COLLECTOR] Scheduler is already running.")
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        self.scheduler = AsyncIOScheduler(event_loop=loop)

        # Schedule periodic job with max_instances=1 to prevent overlapping runs
        trigger = IntervalTrigger(minutes=self.interval_minutes)
        self.scheduler.add_job(
            self.run_collection_cycle,
            trigger=trigger,
            id="periodic_train_collection",
            name="Periodic Train Data Collection",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=60,
        )

        self.scheduler.start()
        logger.info(
            f"[COLLECTOR] Scheduler started with interval of {self.interval_minutes} minute(s) "
            f"for trains: {self.tracked_trains}"
        )

    def stop(self) -> None:
        """Cleanly stop the scheduler on application shutdown."""
        if self.scheduler and self.scheduler.running:
            logger.info("[COLLECTOR] Shutting down collection scheduler...")
            self.scheduler.shutdown(wait=False)
            logger.info("[COLLECTOR] Collection scheduler stopped.")
        self.scheduler = None

    async def run_collection_cycle(self) -> Dict[str, Any]:
        """Execute a single collection cycle for all configured tracked trains.

        Guarantees non-overlapping execution via an internal lock.
        Failure of one train will not stop collection of remaining trains.
        """
        async with self._lock:
            if self._is_cycle_running:
                logger.warning("[COLLECTOR] Previous collection cycle is still running. Skipping overlap.")
                return {"status": "skipped", "reason": "cycle_in_progress"}

            self._is_cycle_running = True

        started_at = datetime.now(IST_TZ).isoformat()
        self.last_collection_started_at = started_at
        self.last_errors = []
        cycle_success_count = 0
        cycle_failure_count = 0

        logger.info("[COLLECTOR] Starting collection cycle")
        collector = get_data_collector()

        try:
            for train_number in self.tracked_trains:
                clean_train = str(train_number).strip()
                if not clean_train:
                    continue

                logger.info(f"[COLLECTOR] Collecting train {clean_train}")
                try:
                    result = await collector.collect_train_observation(clean_train, skip_duplicates=True)
                    cycle_success_count += 1
                    msg = result.get("message", "collected")
                    logger.info(f"[COLLECTOR] Train {clean_train} processed successfully: {msg}")
                except (DataCollectorError, RailwayAPIException) as exc:
                    cycle_failure_count += 1
                    err_msg = str(exc)
                    logger.warning(f"[COLLECTOR] Train {clean_train} failed: {err_msg}")
                    self.last_errors.append(
                        {
                            "train_number": clean_train,
                            "error": err_msg,
                            "timestamp": datetime.now(IST_TZ).isoformat(),
                        }
                    )
                except Exception as exc:
                    cycle_failure_count += 1
                    err_msg = f"Unexpected error: {str(exc)}"
                    logger.error(f"[COLLECTOR] Train {clean_train} encountered unexpected error: {err_msg}")
                    self.last_errors.append(
                        {
                            "train_number": clean_train,
                            "error": err_msg,
                            "timestamp": datetime.now(IST_TZ).isoformat(),
                        }
                    )
        finally:
            completed_at = datetime.now(IST_TZ).isoformat()
            self.last_collection_completed_at = completed_at
            self.last_success_count = cycle_success_count
            self.last_failure_count = cycle_failure_count
            self.total_cycles_run += 1
            self._is_cycle_running = False

            logger.info(
                f"[COLLECTOR] Collection cycle completed: {cycle_success_count} succeeded, "
                f"{cycle_failure_count} failed"
            )

        return {
            "status": "completed",
            "started_at": started_at,
            "completed_at": completed_at,
            "success_count": cycle_success_count,
            "failure_count": cycle_failure_count,
            "errors": self.last_errors,
        }

    def get_status(self) -> Dict[str, Any]:
        """Return the current in-memory collection scheduler status."""
        return {
            "scheduler_running": self.is_running,
            "interval_minutes": self.interval_minutes,
            "tracked_trains": self.tracked_trains,
            "last_collection_started_at": self.last_collection_started_at,
            "last_collection_completed_at": self.last_collection_completed_at,
            "last_success_count": self.last_success_count,
            "last_failure_count": self.last_failure_count,
            "last_errors": self.last_errors,
        }


# Centralized singleton instance
_scheduler_instance: Optional[CollectionScheduler] = None


def get_collection_scheduler() -> CollectionScheduler:
    """Return the centralized singleton CollectionScheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = CollectionScheduler()
    return _scheduler_instance
