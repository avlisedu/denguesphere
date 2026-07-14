"""Tiny in-memory job store for long-running work (geocoding).

Nominatim is rate-limited to ~1 request/second, so geocoding a batch of
any real size takes minutes, not seconds — too long to hold open a
single HTTP request. Jobs run in a background thread; the client polls
for progress instead.

In-process only: fine for a single ml-service instance. If this ever
needs to run as multiple replicas, swap this for Redis-backed state
without changing the router/frontend contract.
"""
import threading
import uuid


class JobStore:
    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, total: int) -> str:
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "status": "running",
                "processed": 0,
                "total": total,
                "result": None,
                "error": None,
            }
        return job_id

    def update_progress(self, job_id: str, processed: int):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id]["processed"] = processed

    def complete(self, job_id: str, result: dict):
        with self._lock:
            self._jobs[job_id]["status"] = "done"
            self._jobs[job_id]["result"] = result

    def fail(self, job_id: str, error: str):
        with self._lock:
            self._jobs[job_id]["status"] = "error"
            self._jobs[job_id]["error"] = error

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None


job_store = JobStore()
